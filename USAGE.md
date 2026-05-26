# 产品经理知识库 - 使用指南

## 项目状态

✅ 项目已完成初始化
✅ 所有模块测试通过
✅ GitHub仓库已配置
✅ 定时任务已配置

## 快速开始

### 1. 配置API Key

编辑 `.env` 文件，填入你的DeepSeek API Key：

```bash
DEEPSEEK_API_KEY=sk-your-api-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

### 2. 推送到GitHub

```bash
# 方式1：使用GitHub CLI
gh auth login
git push -u origin master

# 方式2：使用Personal Access Token
git remote set-url origin https://YOUR_TOKEN@github.com/Sudentking/PM_Knowledge_DB.git
git push -u origin master

# 方式3：使用SSH
git remote set-url origin git@github.com:Sudentking/PM_Knowledge_DB.git
git push -u origin master
```

### 3. 运行工作流

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

### 4. 配置定时任务

**Windows（推荐）**：
```bash
# 方式1：使用任务计划程序
# 1. 打开"任务计划程序"
# 2. 导入 task_definition.xml
# 3. 设置触发器为每天凌晨2点

# 方式2：使用命令行
schtasks /create /tn "ProductManagerKnowledgeDB" /tr "D:\python3.12\python.exe D:\code\Knowledge_DB\scripts\scheduler.py" /sc daily /st 02:00 /f
```

**Linux/Mac**：
```bash
# 编辑crontab
crontab -e

# 添加以下行（每天凌晨2点执行）
0 2 * * * cd /path/to/Knowledge_DB && python3 scripts/workflow.py
```

## 项目结构

```
Knowledge_DB/
├── .env                        # API配置（已git忽略）
├── README.md                   # 项目说明
├── Agent.md                    # 项目进度
├── SETUP.md                    # 配置指南
├── USAGE.md                    # 本文件
├── requirements.txt            # Python依赖
├── config/
│   ├── config.yaml             # 主配置
│   └── categories.yaml         # 分类配置
├── scripts/
│   ├── crawler.py              # 爬虫模块
│   ├── summarizer.py           # AI总结模块
│   ├── workflow.py             # 工作流模块
│   ├── scheduler.py            # 定时任务
│   ├── test_system.py          # 系统测试
│   └── utils/                  # 工具模块
├── data/
│   ├── raw/                    # 原始数据
│   ├── processed/              # 处理后数据
│   └── index.json              # 全局索引
├── knowledge_base/             # 知识库
│   ├── product-design/         # 产品设计
│   ├── user-research/          # 用户研究
│   ├── data-analysis/          # 数据分析
│   ├── project-management/     # 项目管理
│   ├── strategy/               # 产品策略
│   └── industry-insights/      # 行业洞察
└── logs/                       # 运行日志
```

## 核心功能

### 1. 自动爬虫
- 从woshipm.com爬取文章
- 支持多分类爬取
- 自动去重和限速
- 断点续爬

### 2. AI总结
- 使用DeepSeek API生成详细摘要
- 800-1000字总结
- 结构化输出（核心观点、方法论、案例、建议）
- 自动提取关键词

### 3. 知识库管理
- Markdown格式存储
- 混合分类（主题+日期）
- 自动归档
- 版本控制

### 4. 自动同步
- Git自动提交
- 推送到GitHub
- 定时执行

## 常用命令

```bash
# 测试系统
python scripts/test_system.py

# 查看状态
python scripts/workflow.py --mode status

# 运行完整工作流
python scripts/workflow.py

# 仅爬取
python scripts/crawler.py --max-pages 1

# 仅总结
python scripts/summarizer.py --today

# 查看日志
tail -f logs/crawler.log
```

## 配置说明

### config/config.yaml

```yaml
# 爬虫配置
crawler:
  base_url: "https://www.woshipm.com"
  max_pages: 5
  delay_seconds: 2

# AI配置
summarizer:
  provider: "deepseek"
  model: "deepseek-chat"
  max_tokens: 1500

# Git配置
git:
  remote: "origin"
  branch: "master"
  auto_push: true

# 定时任务
schedule:
  cron: "0 2 * * *"
```

## 故障排除

### Q: API调用失败
A: 检查`.env`文件中的API Key是否正确

### Q: 爬虫被封禁
A: 增加`delay_seconds`配置，或配置代理

### Q: Git推送失败
A: 检查GitHub认证，或使用SSH方式

### Q: 定时任务不执行
A: 检查任务计划程序是否启用，或检查cron日志

## 下一步

1. 配置API Key
2. 推送到GitHub
3. 运行测试
4. 启动定时任务
5. 开始使用知识库

## 技术支持

- 查看日志：`logs/crawler.log`
- 运行测试：`python scripts/test_system.py`
- 查看状态：`python scripts/workflow.py --mode status`
