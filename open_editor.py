import sys
import socket
import subprocess
import webbrowser
import time
from pathlib import Path
import os

def is_server_running(port=8000):
    """Check if server is running"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            result = s.connect_ex(('127.0.0.1', port))
            if result == 0:
                print(f"Server detected running on port {port}")
                return True
            if result != 10035:
                print(f"Port {port} not responding")
            return False
    except Exception as e:
        print(f"Error checking server status: {str(e)}")
        return False

def check_dependencies():
    """Check and install required dependencies"""
    try:
        import fastapi
        import uvicorn
        return True
    except ImportError:
        print("Installing required dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn[standard]", "websockets"])
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to install dependencies: {str(e)}")

def start_server():
    """Start the server"""
    server_script = Path(__file__).parent / 'file_sync_server.py'
    
    try:
        print("Starting server...")
        
        # Windows system
        if sys.platform.startswith('win'):
            # Use python.exe instead of pythonw.exe for better error feedback
            python_path = sys.executable
            
            # First try to start server process directly
            process = subprocess.Popen(
                [python_path, str(server_script)],
                # Don't hide window to see errors during startup
                # creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Wait for initialization
            time.sleep(2)
            
            # Check if process is still running
            if process.poll() is not None:
                print("Server process exited abnormally")
                return False
            
        # macOS or Linux systems
        else:
            subprocess.Popen(['python3', str(server_script)],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
            
        # Increase wait time and retry count
        print("Waiting for server response...")
        for i in range(15):  # Increase timeout to 15 seconds
            if is_server_running():
                print("Server started successfully!")
                time.sleep(1)  # Extra wait to ensure server is fully ready
                return True
            if i < 14:  # Don't show wait message for last attempt
                print(f"Waiting... ({i+1}/15)")
            time.sleep(1)
            
        print("Server startup timed out, please check if port 8000 is in use by another program")
        return False
        
    except Exception as e:
        print(f"Error starting server: {str(e)}")
        return False

def open_browser(url):
    """More reliable browser opening method"""
    try:
        # First try using default browser
        if webbrowser.open(url):
            return True
        
        # If default method fails, try common browsers
        browsers = [
            'chrome',
            'msedge', 
            'firefox',
            'safari',
            'opera'
        ]
        
        for browser in browsers:
            try:
                b = webbrowser.get(browser)
                if b.open(url):
                    return True
            except:
                continue
                
        # If still fails, try system commands
        if sys.platform.startswith('win'):
            os.system(f'start {url}')
        elif sys.platform.startswith('darwin'):
            os.system(f'open {url}')
        else:
            os.system(f'xdg-open {url}')
            
        return True
    except Exception as e:
        print(f"Failed to open browser: {str(e)}")
        print(f"Please visit manually: {url}")
        return False

def main():
    if not check_dependencies():
        print("Failed to install required dependencies")
        return

    if not is_server_running():
        print("Starting server...")
        if not start_server():
            print("Server startup failed")
            return

    url = "http://127.0.0.1:8000"
    print("Opening editor...")
    if not open_browser(url):
        print("Please manually open browser and visit:", url)

if __name__ == "__main__":
    main()