# 查看总结内容指南

## 方式1: 使用Obsidian（推荐）

### 为什么选择Obsidian？
- ✅ 原生支持Markdown
- ✅ 强大的搜索功能
- ✅ 支持双向链接
- ✅ 可以建立知识图谱
- ✅ 免费使用

### 配置步骤

**步骤1: 下载Obsidian**
- 访问: https://obsidian.md/
- 下载并安装

**步骤2: 打开知识库**
1. 打开Obsidian
2. 点击 "Open another vault"
3. 选择 "Open folder as vault"
4. 选择 `D:\code\Knowledge_DB\knowledge_base` 文件夹

**步骤3: 配置Obsidian（可选）**

创建 `.obsidian/config.json`：
```json
{
  "showLineNumber": true,
  "strictLineBreaks": false,
  "readableLineLength": true
}
```

### Obsidian使用技巧

**查看文章**:
- 左侧文件树浏览
- 点击文件查看内容
- 使用 `Ctrl+P` 快速打开文件

**搜索内容**:
- `Ctrl+Shift+F` 全局搜索
- 支持正则表达式
- 可以搜索标签

**建立链接**:
- 使用 `[[]]` 创建双向链接
- 使用 `#标签` 添加标签
- 建立知识图谱

**推荐插件**:
- Tag Wrangler: 标签管理
- Dataview: 数据查询
- Calendar: 日历视图
- Graph View: 知识图谱

---

## 方式2: 使用VS Code

### 配置步骤

1. 安装VS Code
2. 安装Markdown插件：
   - Markdown All in One
   - Markdown Preview Enhanced
   - Markdown PDF

3. 打开知识库文件夹：
   ```
   文件 → 打开文件夹 → 选择 knowledge_base
   ```

4. 预览Markdown：
   - `Ctrl+Shift+V` 打开预览
   - `Ctrl+K V` 侧边预览

---

## 方式3: 使用Typora

### 配置步骤

1. 下载Typora: https://typora.io/
2. 打开 `knowledge_base` 文件夹
3. 直接查看和编辑Markdown文件

### Typora优点
- 所见即所得
- 界面简洁
- 支持导出PDF/HTML

---

## 方式4: 使用命令行

### Windows
```bash
# 查看文件列表
dir knowledge_base /s /b

# 查看文件内容
type knowledge_base\product-design\2026-05-26\文章.md

# 使用more分页查看
more knowledge_base\product-design\2026-05-26\文章.md
```

### Linux/Mac
```bash
# 查看文件列表
find knowledge_base -name "*.md"

# 查看文件内容
cat knowledge_base/product-design/2026-05-26/文章.md

# 使用less分页查看
less knowledge_base/product-design/2026-05-26/文章.md
```

---

## 方式5: 使用Web浏览器

### 本地HTTP服务器

```bash
# 安装Python HTTP服务器
pip install mkdocs

# 启动服务器
mkdocs serve

# 访问 http://localhost:8000
```

### 使用GitHub Pages

1. 推送代码到GitHub
2. 启用GitHub Pages
3. 访问 https://username.github.io/repo

---

## 方式6: 使用Pandoc转换格式

### 安装Pandoc
```bash
# Windows
choco install pandoc

# Mac
brew install pandoc

# Linux
sudo apt install pandoc
```

### 转换为PDF
```bash
pandoc knowledge_base/product-design/文章.md -o 文章.pdf
```

### 转换为HTML
```bash
pandoc knowledge_base/product-design/文章.md -o 文章.html
```

### 批量转换
```bash
# Windows
for %f in (knowledge_base\*.md) do pandoc "%f" -o "%~dpnf.html"

# Linux/Mac
for f in knowledge_base/*.md; do pandoc "$f" -o "${f%.md}.html"; done
```

---

## 文件结构说明

```
knowledge_base/
├── product-design/          # 产品设计
│   ├── README.md           # 分类说明
│   └── 2026-05-26/         # 按日期归档
│       └── 文章标题.md      # 总结文件
├── user-research/           # 用户研究
├── data-analysis/           # 数据分析
├── project-management/      # 项目管理
├── strategy/                # 产品策略
└── industry-insights/       # 行业洞察
```

## Markdown文件格式

每个总结文件包含：
```markdown
# 文章标题

**作者**: xxx
**发布时间**: xxx
**原文链接**: [url](url)
**标签**: xxx

---

## 核心观点（200字）
...

## 方法论/框架（300字）
...

## 关键案例（200字）
...

## 实践建议（200字）
...

## 关键词标签
...
```

## 搜索和筛选

### 按分类查看
```
knowledge_base/product-design/   # 产品设计
knowledge_base/user-research/    # 用户研究
knowledge_base/data-analysis/    # 数据分析
```

### 按日期查看
```
knowledge_base/*/2026-05-26/     # 2026年5月26日的文章
```

### 按关键词搜索

**Windows**:
```bash
findstr /s /i "关键词" knowledge_base\*.md
```

**Linux/Mac**:
```bash
grep -r "关键词" knowledge_base/
```

**Obsidian**:
- 使用 `Ctrl+Shift+F` 全局搜索
- 支持正则表达式
- 可以搜索标签

## 推荐工作流

### 日常学习
1. 使用Obsidian打开知识库
2. 浏览最新文章
3. 添加笔记和链接
4. 建立知识图谱

### 深度研究
1. 按分类筛选文章
2. 使用搜索找相关内容
3. 导出为PDF整理
4. 建立专题文档

### 团队协作
1. 使用Git同步知识库
2. 在GitHub上查看
3. 使用Issues讨论
4. 使用PR贡献内容

## 常见问题

### Q: 如何批量重命名文件？
A: 使用PowerShell脚本或Python脚本

### Q: 如何导出所有文章？
A: 使用Pandoc批量转换

### Q: 如何同步到手机？
A: 使用Obsidian Sync或Git同步

### Q: 如何备份知识库？
A: 使用Git推送到GitHub

### Q: 如何分享给他人？
A: 分享GitHub仓库链接
