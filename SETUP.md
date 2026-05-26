# 配置指南

## 快速配置步骤

### 1. 设置OpenAI API Key

**Windows (PowerShell)**:
```powershell
$env:OPENAI_API_KEY="your_api_key_here"
```

**Windows (CMD)**:
```cmd
set OPENAI_API_KEY=your_api_key_here
```

**Linux/Mac**:
```bash
export OPENAI_API_KEY=your_api_key_here
```

**永久设置（推荐）**:
1. 创建 `.env` 文件：
```
OPENAI_API_KEY=your_api_key_here
```

2. 或者添加到系统环境变量

### 2. 配置GitHub远程仓库

```bash
# 初始化Git仓库（已完成）
git init

# 添加远程仓库
git remote add origin https://github.com/yourusername/Knowledge_DB.git

# 首次提交
git add .
git commit -m "Initial commit"
git push -u origin master
```

### 3. 测试系统

```bash
# 运行系统测试
python scripts/test_system.py

# 测试爬虫（仅爬取1页）
python scripts/crawler.py --max-pages 1

# 测试工作流
python scripts/workflow.py --mode status
```

### 4. 配置定时任务

**Windows任务计划程序**:
```bash
# 创建启动脚本
python scripts/scheduler.py --create-scripts

# 创建Windows任务
python scripts/scheduler.py --create-task
```

**Linux cron**:
```bash
# 编辑crontab
crontab -e

# 添加以下行（每天凌晨2点执行）
0 2 * * * cd /path/to/Knowledge_DB && python3 scripts/workflow.py
```

## 配置文件说明

### config/config.yaml

```yaml
# 爬虫配置
crawler:
  base_url: "https://www.woshipm.com"
  max_pages: 5          # 每次爬取的最大页数
  delay_seconds: 2      # 请求间隔（秒）
  timeout: 30           # 请求超时（秒）
  retry_times: 3        # 重试次数

# AI总结配置
summarizer:
  provider: "openai"    # openai / claude
  api_key: "${OPENAI_API_KEY}"
  model: "gpt-4"        # 使用的模型
  max_tokens: 1500      # 最大token数
  temperature: 0.3      # 生成温度

# Git配置
git:
  remote: "origin"      # 远程仓库名称
  branch: "main"        # 分支名称
  auto_push: true       # 自动推送
  commit_message_prefix: "[Knowledge DB]"

# 定时任务配置
schedule:
  enabled: true
  cron: "0 2 * * *"     # 每天凌晨2点
  timezone: "Asia/Shanghai"
```

### config/categories.yaml

定义文章分类和关键词映射，用于自动分类文章。

## 常见问题

### Q: 如何获取OpenAI API Key？
A: 
1. 访问 https://platform.openai.com/
2. 注册/登录账号
3. 进入 API Keys 页面
4. 创建新的 API Key

### Q: 如何使用Claude API？
A: 
1. 修改 `config/config.yaml` 中的 `summarizer.provider` 为 `claude`
2. 设置环境变量 `ANTHROPIC_API_KEY`

### Q: 爬虫被网站封禁怎么办？
A: 
1. 增加 `delay_seconds` 配置
2. 配置代理服务器
3. 减少 `max_pages` 配置

### Q: 如何查看日志？
A: 
```bash
# 查看实时日志
tail -f logs/crawler.log

# Windows
Get-Content logs/crawler.log -Wait
```

### Q: 如何手动触发爬取？
A: 
```bash
# 完整工作流
python scripts/workflow.py

# 仅爬取
python scripts/crawler.py

# 仅总结
python scripts/summarizer.py --today
```

### Q: 如何查看系统状态？
A: 
```bash
python scripts/workflow.py --mode status
```

## 下一步

1. 配置 API Key
2. 连接 GitHub 仓库
3. 运行测试
4. 启动定时任务
5. 开始使用知识库
