from fastapi import FastAPI, WebSocket, HTTPException, Request, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
import signal
import time
import sys
from contextlib import asynccontextmanager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='sync.log'
)

# 使用新的生命周期事件语法
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    print("Server starting...")
    logging.info("Server starting")
    
    # 初始化资源
    try:
        # 创建备份目录
        backup_dir.mkdir(exist_ok=True)
        
        # 启动空闲检查任务
        idle_check_task = asyncio.create_task(ServerManager.check_idle())
        
        # 注册信号处理
        def signal_handler(signum, frame):
            logging.info(f"Received signal {signum}, preparing to shut down...")
            asyncio.create_task(ServerManager.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        logging.info("Server initialization complete")
        yield
        
    except Exception as e:
        logging.error(f"Server startup error: {str(e)}")
        raise
    finally:
        # 关闭时执行
        print("Server shutting down...")
        logging.info("Server beginning shutdown")
        
        try:
            # 取消空闲检查任务
            idle_check_task.cancel()
            
            # 关闭所有 WebSocket 连接
            for connections in active_connections.values():
                for ws in connections:
                    try:
                        await ws.close()
                    except Exception:
                        pass
            
            # 清理资源
            active_connections.clear()
            file_locks.clear()
            FileSync._chunks.clear()
            
            logging.info("Server has fully shut down")
            
        except Exception as e:
            logging.error(f"Error during server shutdown: {str(e)}")

# 创建 FastAPI 应用
app = FastAPI(lifespan=lifespan)

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
app.mount("/static", StaticFiles(directory="static"), name="static")

# 全局变量
active_connections: Dict[str, List[WebSocket]] = {}  # WebSocket连接
file_locks: Dict[str, asyncio.Lock] = {}  # 文件锁
backup_dir = Path('backups')  # 备份目录
backup_dir.mkdir(exist_ok=True)
last_activity_time = datetime.now()
shutdown_timer = None
SHUTDOWN_DELAY = 300  # 5分钟无活动后关闭

class FileManager:
    @staticmethod
    async def create_backup(file_id: str, content: str):
        """创建文件备份"""
        try:
            backup_path = backup_dir / file_id
            backup_path.mkdir(exist_ok=True)
            
            # 检查内容是否有实质变化
            backups = sorted(backup_path.glob('*.bak'))
            if backups:
                latest_backup = backups[-1]
                latest_content = latest_backup.read_text(encoding='utf-8')
                if latest_content.strip() == content.strip():
                    return  # 内容未变化，不创建备份
                
                # 缩短备份间隔到1分钟
                backup_time = datetime.fromtimestamp(float(latest_backup.stem))
                if (datetime.now() - backup_time).total_seconds() < 60*5:  # 1分钟
                    return
            
            # 创建新备份
            timestamp = datetime.now().timestamp()
            backup_file = backup_path / f"{timestamp}.bak"
            backup_file.write_text(content, encoding='utf-8')
            
            # 增加备份数量到50个
            backups = sorted(backup_path.glob('*.bak'))
            if len(backups) > 50:
                for old_backup in backups[:-50]:
                    old_backup.unlink()
        except Exception as e:
            logging.error(f"Error creating backup: {str(e)}")

async def broadcast_to_clients(file_id: str, content: str, exclude_ws: WebSocket = None):
    """广播内容到所有连接的客户端"""
    if file_id in active_connections:
        for ws in active_connections[file_id]:
            if ws != exclude_ws and ws.client_state.CONNECTED:
                try:
                    await ws.send_json({"type": "update", "content": content})
                except Exception as e:
                    logging.error(f"Error broadcasting to client: {str(e)}")

class ServerManager:
    @staticmethod
    async def check_idle():
        """检查服务器空闲状态"""
        while True:
            await asyncio.sleep(60)  # 每分钟检查一次
            if not active_connections:
                idle_time = (datetime.now() - last_activity_time).total_seconds()
                if idle_time > SHUTDOWN_DELAY:
                    logging.info("Server idle for over 5 minutes, preparing to shut down...")
                    await ServerManager.shutdown()
                    break

    @staticmethod
    async def shutdown():
        """优雅关闭服务器"""
        try:
            # 通知所有客户端
            for connections in active_connections.values():
                for ws in connections:
                    try:
                        await ws.send_json({
                            "type": "shutdown",
                            "message": "Server is shutting down, please save your changes"
                        })
                        await ws.close()
                    except Exception:
                        pass
            
            # 等待所有连接关闭
            await asyncio.sleep(2)
            
            # 清理资源
            active_connections.clear()
            file_locks.clear()
            
            logging.info("Server has safely shut down")
            sys.exit(0)
        except Exception as e:
            logging.error(f"Error during server shutdown: {str(e)}")
            sys.exit(1)

class FileSync:
    _chunks = {}
    
    @staticmethod
    async def handle_incremental_update(file_id: str, start: int, content: str, old_length: int):
        """处理增量更新"""
        try:
            async with file_locks[file_id]:
                await broadcast_to_clients(file_id, {
                    "type": "incremental_update",
                    "start": start,
                    "content": content,
                    "oldLength": old_length
                })
        except Exception as e:
            logging.error(f"Error handling incremental update: {str(e)}")
    
    @staticmethod
    async def handle_chunked_update(file_id: str, chunk_data: dict):
        """处理分块更新"""
        try:
            if chunk_data["type"] == "chunked_edit_start":
                FileSync._chunks[file_id] = {
                    "content": [""] * chunk_data["totalChunks"],
                    "received": 0,
                    "total": chunk_data["totalChunks"]
                }
            elif chunk_data["type"] == "chunked_edit_chunk":
                chunk_num = chunk_data["chunk"]
                FileSync._chunks[file_id]["content"][chunk_num] = chunk_data["content"]
                FileSync._chunks[file_id]["received"] += 1
                
                # 检查是否收到所有块
                if FileSync._chunks[file_id]["received"] == FileSync._chunks[file_id]["total"]:
                    complete_content = "".join(FileSync._chunks[file_id]["content"])
                    await broadcast_to_clients(file_id, {
                        "type": "update",
                        "content": complete_content
                    })
                    del FileSync._chunks[file_id]
        except Exception as e:
            logging.error(f"Error handling chunked update: {str(e)}")

@app.websocket("/ws/{file_id}")
async def websocket_endpoint(websocket: WebSocket, file_id: str):
    global last_activity_time
    try:
        await websocket.accept()
        if file_id not in file_locks:
            file_locks[file_id] = asyncio.Lock()
        if file_id not in active_connections:
            active_connections[file_id] = []

        active_connections[file_id].append(websocket)
        last_activity_time = datetime.now()
        
        try:
            while True:
                data = await websocket.receive_json()
                last_activity_time = datetime.now()  # 更新活动时间
                
                if data["type"] == "incremental_edit":
                    await FileSync.handle_incremental_update(
                        file_id, 
                        data["start"], 
                        data["content"], 
                        data["oldLength"]
                    )
                elif data["type"] in ["chunked_edit_start", "chunked_edit_chunk"]:
                    await FileSync.handle_chunked_update(file_id, data)
                elif data["type"] == "edit":
                    # 处理普通更新
                    await broadcast_to_clients(file_id, data["content"], websocket)
        except Exception as e:
            logging.error(f"WebSocket error: {str(e)}")
        finally:
            active_connections[file_id].remove(websocket)
            if not active_connections[file_id]:
                del active_connections[file_id]
                del file_locks[file_id]
    except Exception as e:
        logging.error(f"WebSocket connection error: {str(e)}")
        await websocket.close()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    logging.error(f"Global error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.get("/")
async def root():
    """返回主页HTML"""
    with open('static/index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    return HTMLResponse(content=content)

@app.get("/api/backups/{file_id}")
async def list_backups(file_id: str):
    """列出文件的所有备份"""
    try:
        backup_path = backup_dir / file_id
        if not backup_path.exists():
            return {"backups": []}
        
        backups = []
        for backup in sorted(backup_path.glob('*.bak')):
            timestamp = float(backup.stem)
            date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            backups.append({
                "timestamp": timestamp,
                "date": date,
                "path": str(backup.relative_to(backup_dir))
            })
        return {"backups": backups}
    except Exception as e:
        logging.error(f"Error listing backups: {str(e)}")
        raise HTTPException(status_code=500, detail="Error listing backups")

@app.get("/api/backups/{file_id}/{timestamp}")
async def get_backup(file_id: str, timestamp: str):
    """获取特定备份的内容"""
    try:
        backup_file = backup_dir / file_id / f"{timestamp}.bak"
        if not backup_file.exists():
            raise HTTPException(status_code=404, detail="Backup not found")
        return {"content": backup_file.read_text(encoding='utf-8')}
    except Exception as e:
        logging.error(f"Error reading backup: {str(e)}")
        raise HTTPException(status_code=500, detail="Error reading backup")



if __name__ == "__main__":
    print("Starting server...")
    try:
        # 使用 uvicorn 启动服务器
        import uvicorn
        print("Starting uvicorn server at http://127.0.0.1:8000")
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        print(traceback.format_exc())