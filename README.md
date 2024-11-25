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
- **快捷键**: Ctrl+B 一键查看历史版本，Ctrl+P 切换预览/编辑模式
- **魔法棒增强预览**: 
  - Markdown 一键美化排版
  - LaTeX 数学公式实时渲染
  - 代码高亮显示
  - 任务列表可视化
  - 表格自动对齐
  - Emoji 表情支持 😄
  - 脚注、上下标完美支持

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

4. **白嫖攻略**
   - **搜索增强**
     1. 在浏览器中安装 Google 搜索增强插件
     2. 打开 ByEdit，拖入你的文档
     3. 选中文本自动触发搜索
     4. 享受高级搜索功能

   - **AI 写作助手**
     1. 安装 Grammarly 插件（免费版即可）
     2. 在 ByEdit 中编辑文档
     3. 自动获得专业版功能
     4. 语法纠错、同义词、风格建议全都有

   - **翻译神器**
     1. 安装你喜欢的翻译插件
     2. ByEdit 自动同步文本
     3. 实时翻译、双语对照
     4. 多个翻译引擎随意切换

   - **AI 对话**
     1. 安装 ChatGPT/Claude 插件
     2. 选中文本一键发送给 AI
     3. 获得即时回复和建议
     4. 多个 AI 助手协同工作

5. **插件推荐**
   - Google Search Extra
   - Grammarly
   - DeepL 翻译
   - 沉浸式翻译
   - ChatGPT for Google
   - Claude Chrome Extension
   - Gemini AI Assistant

   
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
   - `Ctrl+P`: 切换预览/编辑模式
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