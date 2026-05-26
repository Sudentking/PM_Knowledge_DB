# 工作流可复现性指南

## 环境要求

### Python环境
- Python版本: 3.9+ (当前使用: 3.12.2)
- 操作系统: Windows/Linux/Mac

### 依赖包
```
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
openai>=1.0.0
pyyaml>=6.0
python-dotenv>=1.0.0
loguru>=0.7.0
gitpython>=3.1.0
fake-useragent>=1.4.0
```

## 复现步骤

### 步骤1: 克隆仓库
```bash
git clone https://github.com/Sudentking/PM_Knowledge_DB.git
cd PM_Knowledge_DB
```

### 步骤2: 创建虚拟环境（推荐）
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 步骤3: 安装依赖
```bash
pip install -r requirements.txt
```

### 步骤4: 配置环境变量
创建 `.env` 文件：
```bash
# DeepSeek API配置
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com

# GitHub配置（可选，用于自动推送）
GITHUB_TOKEN=your_github_token
```

### 步骤5: 测试系统
```bash
python scripts/test_system.py
```

预期输出：
```
通过率: 6/6 (100.0%)
所有测试通过！系统准备就绪。
```

### 步骤6: 运行工作流
```bash
# 完整工作流（爬取+总结+推送）
python scripts/workflow.py

# 仅爬取
python scripts/crawler.py

# 仅总结
python scripts/summarizer.py --today

# 查看状态
python scripts/workflow.py --mode status
```

## 配置说明

### 爬虫配置 (config/config.yaml)
```yaml
crawler:
  base_url: "https://www.woshipm.com"
  categories:
    - "pd"           # 产品设计
    - "ai"           # 人工智能
    - "it"           # 信息技术
  max_pages: 5       # 每个分类爬取的页数
  delay_seconds: 2   # 请求间隔（秒）
```

### AI总结配置
```yaml
summarizer:
  provider: "deepseek"
  api_key: "${DEEPSEEK_API_KEY}"
  base_url: "${DEEPSEEK_BASE_URL}"
  model: "deepseek-chat"
  max_tokens: 1500
  temperature: 0.3
```

### Git配置
```yaml
git:
  remote: "origin"
  branch: "master"
  auto_push: true
```

## 输出文件说明

### 原始数据
```
data/raw/YYYY-MM-DD/
├── article_id.json    # 原始文章数据
```

### 总结数据
```
data/processed/YYYY-MM-DD/
├── article_id_summary.json  # AI总结结果
```

### 知识库
```
knowledge_base/
├── product-design/    # 产品设计
├── user-research/     # 用户研究
├── data-analysis/     # 数据分析
├── project-management/# 项目管理
├── strategy/          # 产品策略
└── industry-insights/ # 行业洞察
```

### 日志
```
logs/
└── crawler.log        # 运行日志
```

## 验证复现

### 检查1: 文件结构
```bash
# 应该看到以下目录
ls -la
# config/ scripts/ data/ knowledge_base/ logs/
```

### 检查2: 配置文件
```bash
# 检查配置文件是否存在
cat config/config.yaml
cat .env
```

### 检查3: 运行测试
```bash
python scripts/test_system.py
# 预期: 通过率 100%
```

### 检查4: 查看日志
```bash
# Windows
type logs\crawler.log

# Linux/Mac
cat logs/crawler.log
```

### 检查5: 查看知识库
```bash
# 查看总结文件
ls data/processed/

# 查看知识库文章
ls knowledge_base/
```

## 常见问题

### Q1: 依赖安装失败
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q2: API调用失败
检查 `.env` 文件中的API Key是否正确：
```bash
# Windows
type .env

# Linux/Mac
cat .env
```

### Q3: 爬虫被封禁
增加请求间隔：
```yaml
# config/config.yaml
crawler:
  delay_seconds: 5  # 增加到5秒
```

### Q4: Git推送失败
检查GitHub Token：
```bash
git remote -v
# 应该显示包含token的URL
```

### Q5: 编码问题（Windows）
设置环境变量：
```bash
set PYTHONIOENCODING=utf-8
```

## 完整复现脚本

### Windows (setup.bat)
```batch
@echo off
echo 正在设置环境...

REM 克隆仓库
git clone https://github.com/Sudentking/PM_Knowledge_DB.git
cd PM_Knowledge_DB

REM 创建虚拟环境
python -m venv venv
call venv\Scripts\activate.bat

REM 安装依赖
pip install -r requirements.txt

REM 创建.env文件
echo DEEPSEEK_API_KEY=your_key_here > .env
echo DEEPSEEK_BASE_URL=https://api.deepseek.com >> .env

REM 运行测试
python scripts/test_system.py

echo 设置完成！
pause
```

### Linux/Mac (setup.sh)
```bash
#!/bin/bash
echo "正在设置环境..."

# 克隆仓库
git clone https://github.com/Sudentking/PM_Knowledge_DB.git
cd PM_Knowledge_DB

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 创建.env文件
cat > .env << EOF
DEEPSEEK_API_KEY=your_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
EOF

# 运行测试
python scripts/test_system.py

echo "设置完成！"
```

## 技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| 爬虫 | requests + BeautifulSoup | 2.31+ / 4.12+ |
| AI总结 | DeepSeek API | deepseek-chat |
| 数据存储 | JSON + Markdown | - |
| 版本控制 | Git + GitHub | - |
| 日志 | loguru | 0.7+ |
| 配置 | YAML + dotenv | - |

## 更新日志

- 2026-05-26: 项目初始化，完成爬虫和AI总结模块
- 2026-05-27: 添加可复现性文档

## 联系方式

- GitHub: https://github.com/Sudentking/PM_Knowledge_DB.git
