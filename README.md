# ByEdit - 让你的编辑器秒变"外挂神器"

[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

ByEdit 是一个黑科技级的编辑器伴侣，让你能够在 VSCode、Obsidian、TeXLive 等本地编辑器中"白嫖"各种超强浏览器插件（比如 Grammarly、Google Translate、沉浸式翻译等）。

## 🌟 主要特性

- **实时同步**: 本地编辑器和浏览器内容双向同步，快得连眨眼都来不及
- **全面兼容**: 支持各路浏览器神器
  - Grammarly 帮你改错字
  - Google Translate 来回切换
  - 沉浸式翻译助你秒变双语达人
  - 更多插件等你来撸...
- **稳如老狗**: 自动备份让你永不丢词
- **傻瓜操作**: 拖个文件就能开始浪
- **快捷键**: Ctrl+B 一键查看历史版本

## 🚀 快速开始

1. **安装**
   ```bash
   # 运行安装脚本
   setup.bat
   ```

2. **启动编辑器**
 - 双击 `edit.bat` 即可启动
 - 或在命令行中运行
   ```bash
   # CMD
   edit

   # PowerShell
   .\edit
   ```

3. **使用方法**
   - 在本地使用 VSCode 等编辑器打开文件
   - 同时在浏览器中打开 http://localhost:8000
   - 拖拽文件到浏览器窗口
   - 开始编辑！

## 💻 系统要求

- Python 3.7+
- 支持的操作系统：Windows
- 现代浏览器（Chrome、Edge、Firefox 等）

## 🛠️ 依赖项

- fastapi
- uvicorn[standard]
- websockets
- python-multipart

## 📝 许可证

[GPL-3.0 License](LICENSE) - 使用需遵循以下规则：
- 任何基于本项目的衍生作品必须开源
- 修改后的代码必须使用相同的 GPL-3.0 协议
- 需要在明显位置标注原作者信息
- 商业使用必须开源

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 🎯 使用提示

1. **最佳实践**
   - 用你最爱的编辑器码字
   - 让浏览器插件帮你润色
   - 备份随时在线保护你的杰作

2. **性能优化**
   - 自动调整同步频率
   - 大文件支持增量同步
   - 智能备份管理

3. **快捷键**
   - `Ctrl+B`: 显示/隐藏备份面板

## ⚠️ 注意事项

- 首次启动可能需要安装依赖
- 确保端口 8000 未被占用
- 建议定期检查备份

## 💻 支持的编辑器

- VSCode
- Obsidian
- TeXLive
- Typora
- 以及任何能编辑文本的软件！