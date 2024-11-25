/**
 * PreviewRenderer 类
 * 用于渲染 Markdown 和 LaTeX 文档的预览
 */
class PreviewRenderer {
    /**
     * 构造函数
     * 初始化 Markdown 解析器和 KaTeX 配置
     */
    constructor() {
        // 初始化 Markdown 解析器及其插件
        this.markdownIt = window.markdownit({
            html: true,
            xhtmlOut: true,
            breaks: true,
            linkify: true,
            typographer: true,
            quotes: '""',
            highlight: function (str, lang) {
                if (lang && hljs.getLanguage(lang)) {
                    try {
                        return hljs.highlight(str, { language: lang }).value;
                    } catch (__) {}
                }
                return '';
            }
        })
        .use(window.markdownitTaskLists, { enabled: true, label: true, labelAfter: true })
        .use(window.markdownitSup)
        .use(window.markdownitSub)
        .use(window.markdownitFootnote)
        .use(window.markdownitEmoji);

        // 自定义表格渲染规则
        this.markdownIt.renderer.rules.table_open = () => '<div class="table-container"><table>';
        this.markdownIt.renderer.rules.table_close = () => '</table></div>';

        // KaTeX 配置
        this.katexConfig = {
            displayMode: true,
            throwOnError: false,
            trust: true,
            strict: false,
            macros: {
                "\\usepackage": "\\text{#1}",  // 处理包引入
                "\\hyphenation": "\\text{#1}", // 处理断字设置
                "\\textcolor": "\\color{#1}{#2}",
                "\\colorbox": "\\bbox[background:#1]{#2}",
                "\\newline": "\\\\",
                "\\newpage": "\\text{\\pagebreak}",
                "\\item": "•",
                "\\R": "\\mathbb{R}",
                "\\N": "\\mathbb{N}",
                "\\Z": "\\mathbb{Z}",
                "\\Q": "\\mathbb{Q}",
                "\\C": "\\mathbb{C}",
            }
        };

        // 算法环境计数器
        this.algorithmCounter = 0;
    }

    /**
     * 根据文件类型选择渲染方式
     */
    render(content, fileType) {
        switch(fileType.toLowerCase()) {
            case 'md':
            case 'markdown':
                return this.renderMarkdown(content);
            case 'tex':
            case 'latex':
                return this.renderLatex(content);
            default:
                return this.renderPlainText(content);
        }
    }

    /**
     * Markdown 渲染
     */
    renderMarkdown(content) {
        try {
            content = this.preprocessContent(content);
            
            const html = this.markdownIt.render(content);
            
            return `
                <div class="markdown-body">
                    ${html}
                </div>
            `;
        } catch (err) {
            console.error('Markdown rendering error:', err);
            return `<pre>${content}</pre>`;
        }
    }

    /**
     * Markdown 内容预处理
     */
    preprocessContent(content) {
        content = content
            .replace(/\*\*/g, '**')
            .replace(/_/g, '_')
            .replace(/~~/g, '~~');
        
        return content;
    }

    /**
     * LaTeX 渲染
     */
    renderLatex(content) {
        try {
            const [preamble, ...bodyParts] = content.split('\\begin{document}');
            let body = bodyParts.join('\\begin{document}');

            // 处理各种 LaTeX 环境和命令
            body = this.processLatexEnvs(body);
            body = this.processLatexCommands(body);
            body = this.processLatexMathEnvs(body);
            body = this.processLatexInlineMath(body);
            body = this.processLatexDisplayMath(body);
            body = this.processAlgorithmEnv(body);

            return `<div class="latex-content"><p>${body}</p></div>`;
        } catch (err) {
            console.error('LaTeX rendering error:', err);
            return `<pre>${content}</pre>`;
        }
    }

    /**
     * 处理 LaTeX 环境
     */
    processLatexEnvs(content) {
        const environments = {
            'theorem': { class: 'theorem', prefix: '定理' },
            'lemma': { class: 'theorem', prefix: '引理' },
            'proposition': { class: 'theorem', prefix: '命题' },
            'corollary': { class: 'theorem', prefix: '推论' },
            'definition': { class: 'definition', prefix: '定义' },
            'proof': { class: 'proof', prefix: '证明' },
            'example': { class: 'example', prefix: '例' },
            'remark': { class: 'remark', prefix: '注' },
            'itemize': { type: 'list', tag: 'ul' },
            'enumerate': { type: 'list', tag: 'ol' },
            'quote': { type: 'block', tag: 'blockquote' },
            'verbatim': { type: 'code', tag: 'pre' }
        };

        Object.entries(environments).forEach(([env, config]) => {
            const regex = new RegExp(`\\\\begin{${env}}([\\s\\S]*?)\\\\end{${env}}`, 'g');
            content = content.replace(regex, (match, inner) => {
                if (config.type === 'list') {
                    const items = inner.split('\\item').filter(item => item.trim());
                    const itemsHtml = items.map(item => `<li>${item.trim()}</li>`).join('');
                    return `<${config.tag}>${itemsHtml}</${config.tag}>`;
                } else if (config.type === 'block') {
                    return `<${config.tag}>${inner.trim()}</${config.tag}>`;
                } else if (config.type === 'code') {
                    return `<pre><code>${inner.trim()}</code></pre>`;
                } else {
                    return `
                        <div class="${config.class}">
                            <strong>${config.prefix}:</strong>
                            ${inner.trim()}
                        </div>
                    `;
                }
            });
        });

        return content;
    }

    /**
     * 处理 LaTeX 命令
     */
    processLatexCommands(content) {
        return content
            // 文本格式
            .replace(/\\textbf\{([^}]+)\}/g, '<strong>$1</strong>')
            .replace(/\\textit\{([^}]+)\}/g, '<em>$1</em>')
            .replace(/\\underline\{([^}]+)\}/g, '<u>$1</u>')
            .replace(/\\texttt\{([^}]+)\}/g, '<code>$1</code>')
            // 引用和参考
            .replace(/\\cite\{([^}]+)\}/g, '[<span class="citation">$1</span>]')
            .replace(/\\ref\{([^}]+)\}/g, '<span class="reference">$1</span>')
            .replace(/\\label\{([^}]+)\}/g, '<span class="label" id="$1"></span>')
            // 空格和换行
            .replace(/~/g, '&nbsp;')
            .replace(/\\quad/g, '&nbsp;&nbsp;')
            .replace(/\\qquad/g, '&nbsp;&nbsp;&nbsp;&nbsp;')
            .replace(/\\\\/g, '<br>')
            // 特殊字符
            .replace(/\\LaTeX/g, 'LaTeX')
            .replace(/\\TeX/g, 'TeX')
            // 颜色支持
            .replace(/\\textcolor\{([^}]+)\}\{([^}]+)\}/g, '<span style="color: $1">$2</span>')
            // URL
            .replace(/\\url\{([^}]+)\}/g, '<a href="$1">$1</a>')
            .replace(/\\href\{([^}]+)\}\{([^}]+)\}/g, '<a href="$1">$2</a>');
    }

    /**
     * 处理 LaTeX 数学环境
     */
    processLatexMathEnvs(content) {
        // 支持的数学环境列表
        const mathEnvs = [
            'equation', 'equation*',
            'align', 'align*',
            'matrix', 'pmatrix',
            'cases', 'gather',
            'split', 'multline',
            'array', 'tabular',
            'subequations'
        ];

        // 处理 amsmath 环境
        mathEnvs.forEach(env => {
            const regex = new RegExp(`\\\\begin\\{${env}\\}([\\s\\S]*?)\\\\end\\{${env}\\}`, 'g');
            content = content.replace(regex, (match, tex) => {
                try {
                    return katex.renderToString(tex.trim(), {
                        ...this.katexConfig,
                        displayMode: true
                    });
                } catch (e) {
                    console.warn(`LaTeX ${env} parse error:`, e);
                    return `<div class="math-error">${match}</div>`;
                }
            });
        });

        // 处理特殊命令
        content = content
            .replace(/\\section\{([^}]+)\}/g, '<h2>$1</h2>')
            .replace(/\\subsection\{([^}]+)\}/g, '<h3>$1</h3>')
            .replace(/\\subsubsection\{([^}]+)\}/g, '<h4>$1</h4>')
            .replace(/\\textbf\{([^}]+)\}/g, '<strong>$1</strong>')
            .replace(/\\textit\{([^}]+)\}/g, '<em>$1</em>')
            .replace(/\\cite\{([^}]+)\}/g, '[<span class="citation">$1</span>]')
            .replace(/\\begin{abstract}([\s\S]*?)\\end{abstract}/g, '<div class="abstract"><h3>摘要</h3>$1</div>');

        return content;
    }

    /**
     * 处理 LaTeX 行内数学公式
     */
    processLatexInlineMath(content) {
        // 处理 $...$ 和 \(...\) 行内公式
        content = content.replace(/\$([^\$]+?)\$/g, (match, tex) => {
            try {
                return katex.renderToString(tex.trim(), {
                    ...this.katexConfig,
                    displayMode: false
                });
            } catch (e) {
                console.warn('LaTeX inline parse error:', e);
                return `<span class="math-error">${match}</span>`;
            }
        });

        content = content.replace(/\\\((.*?)\\\)/g, (match, tex) => {
            try {
                return katex.renderToString(tex.trim(), {
                    ...this.katexConfig,
                    displayMode: false
                });
            } catch (e) {
                console.warn('LaTeX inline parse error:', e);
                return `<span class="math-error">${match}</span>`;
            }
        });

        return content;
    }

    /**
     * 处理 LaTeX 显示数学公式
     */
    processLatexDisplayMath(content) {
        // 处理 $$...$$ 和 \[...\] 显示公式
        content = content.replace(/\$\$([\s\S]+?)\$\$/g, (match, tex) => {
            try {
                return katex.renderToString(tex.trim(), {
                    ...this.katexConfig,
                    displayMode: true
                });
            } catch (e) {
                console.warn('LaTeX display parse error:', e);
                return `<div class="math-error">${match}</div>`;
            }
        });

        content = content.replace(/\\\[([\s\S]+?)\\\]/g, (match, tex) => {
            try {
                return katex.renderToString(tex.trim(), {
                    ...this.katexConfig,
                    displayMode: true
                });
            } catch (e) {
                console.warn('LaTeX display parse error:', e);
                return `<div class="math-error">${match}</div>`;
            }
        });

        return content;
    }

    /**
     * 渲染纯文本
     */
    renderPlainText(content) {
        return `<pre>${content}</pre>`;
    }

    /**
     * 获取文件类型
     */
    getFileType(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        return ext;
    }

    /**
     * 处理算法环境（只支持 algorithm2e）
     */
    processAlgorithmEnv(content) {
        return content.replace(/\\begin{algorithm}\s*([\s\S]*?)\\end{algorithm}/g, 
            (match, body) => {
                try {
                    // 处理标题和标签
                    const captionMatch = body.match(/\\caption\{([^}]+)\}/);
                    const labelMatch = body.match(/\\label\{([^}]+)\}/);
                    const title = captionMatch ? captionMatch[1] : '';
                    
                    // 预处理算法命令
                    body = body
                        // 移除标题和标签（已单独处理）
                        .replace(/\\caption\{[^}]+\}/g, '')
                        .replace(/\\label\{[^}]+\}/g, '')
                        // 基础设置
                        .replace(/\\SetAlgoLined/g, '')
                        // 输入输出
                        .replace(/\\KwIn\{([^}]+)\}/g, '<div class="algorithm-input">Input: $1</div>')
                        .replace(/\\KwOut\{([^}]+)\}/g, '<div class="algorithm-output">Output: $1</div>')
                        // 注释
                        .replace(/\\tcp\*?\{([^}]+)\}/g, '<span class="algorithm-comment">// $1</span>')
                        // 控制结构
                        .replace(/\\For\{([^}]+)\s+\\KwTo\s+([^}]+)\}/g, '<div class="algorithm-for">for $1 to $2</div>')
                        .replace(/\\While\{([^}]+)\}/g, '<div class="algorithm-while">while $1</div>')
                        .replace(/\\eIf\{([^}]+)\}/g, '<div class="algorithm-if">if $1</div>')
                        .replace(/\\If\{([^}]+)\}/g, '<div class="algorithm-if">if $1</div>')
                        .replace(/\\ElseIf\{([^}]+)\}/g, '<div class="algorithm-if">else if $1</div>')
                        .replace(/\\Else/g, '<div class="algorithm-else">else</div>')
                        // 返回语句
                        .replace(/\\Return\{([^}]+)\}/g, '<div class="algorithm-return">return $1</div>')
                        // 数学符号
                        .replace(/\$([^$]+)\$/g, '<span class="math">$1</span>')
                        .replace(/\\leftarrow/g, '←')
                        .replace(/\\rightarrow/g, '→')
                        .replace(/\\gets/g, '←')
                        // 集合符号
                        .replace(/\\{/g, '{')
                        .replace(/\\}/g, '}')
                        // 变量赋值
                        .replace(/([a-zA-Z0-9_]+)\s*←\s*([^\\]+)(?=\\|$)/g, 
                            '<div class="algorithm-assign">$1 ← $2</div>')
                        // 清理
                        .replace(/\\;/g, '')
                        .replace(/\n\s*\n/g, '\n')
                        // 处理普通语句
                        .replace(/^([^<\n][^\n]+)$/gm, '<div class="algorithm-state">$1</div>');
    
                    // 构建最终HTML
                    return `
                        <div class="algorithm">
                            ${title ? `<div class="algorithm-title">${title}</div>` : ''}
                            <div class="algorithm-body">
                                ${body.trim()}
                            </div>
                        </div>`;
                } catch (e) {
                    console.warn('Algorithm parse error:', e);
                    return `<div class="algorithm-error">${match}</div>`;
                }
            });
    }
}