# 产品经理知识库 (Product Manager Knowledge DB)

一个自动化的产品经理知识管理系统，从人人都是产品经理网站（woshipm.com）爬取文章，通过AI生成详细摘要，并同步到GitHub远程仓库。

## 特性

- **自动爬取**：定时从woshipm.com爬取最新文章
- **AI总结**：使用GPT-4生成800-1000字的详细摘要
- **混合分类**：一级目录按主题，二级目录按日期
- **可迁移**：Markdown格式，任何平台都能读取
- **可扩展**：模块化设计，易于添加新功能
- **版本控制**：Git管理，支持历史回溯

## 目录结构

```
Knowledge_DB/
├── README.md                          # 项目说明
├── Agent.md                           # 项目进度记录
├── .gitignore                         # Git配置
├── requirements.txt                   # Python依赖
├── config/
│   ├── config.yaml                    # 主配置文件
│   └── categories.yaml                # 分类配置
├── scripts/
│   ├── crawler.py                     # 爬虫脚本
│   ├── summarizer.py                  # AI总结脚本
│   ├── workflow.py                    # 工作流脚本
│   └── utils/                         # 工具模块
├── data/
│   ├── raw/                           # 原始数据
│   ├── processed/                     # 处理后数据
│   └── index.json                     # 全局索引
├── knowledge_base/                    # 知识库
│   ├── product-design/                # 产品设计
│   ├── user-research/                 # 用户研究
│   ├── data-analysis/                 # 数据分析
│   ├── project-management/            # 项目管理
│   ├── strategy/                      # 产品策略
│   └── industry-insights/             # 行业洞察
└── logs/                              # 运行日志
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# Windows
set OPENAI_API_KEY=your_api_key_here

# Linux/Mac
export OPENAI_API_KEY=your_api_key_here
```

### 3. 运行工作流

```bash
# 完整工作流（爬取+总结+上传）
python scripts/workflow.py

# 仅爬取
python scripts/crawler.py

# 仅总结（处理已爬取的数据）
python scripts/summarizer.py
```

### 4. 配置定时任务

#### Windows（任务计划程序）
1. 打开"任务计划程序"
2. 创建基本任务
3. 设置每天凌晨2点执行
4. 程序：`python`
5. 参数：`D:\code\Knowledge_DB\scripts\workflow.py`

#### Linux（cron）
```bash
crontab -e
# 添加以下行：
0 2 * * * cd /path/to/Knowledge_DB && python scripts/workflow.py
```

## 配置说明

### 主配置文件 (`config/config.yaml`)

```yaml
crawler:
  base_url: "https://www.woshipm.com"
  max_pages: 5
  delay_seconds: 2

summarizer:
  provider: "openai"
  model: "gpt-4"
  max_tokens: 1500

git:
  auto_push: true
  branch: "main"

schedule:
  cron: "0 2 * * *"
```

### 分类配置 (`config/categories.yaml`)

支持6个主要分类：
- 产品设计 (product-design)
- 用户研究 (user-research)
- 数据分析 (data-analysis)
- 项目管理 (project-management)
- 产品策略 (strategy)
- 行业洞察 (industry-insights)

## 使用场景

1. **日常学习**：每天自动获取最新的产品经理文章精华
2. **知识沉淀**：将碎片化知识整理成结构化文档
3. **团队共享**：通过Git仓库共享给团队成员
4. **个人成长**：建立自己的产品经理知识体系

## 注意事项

1. 请确保有有效的OpenAI API Key
2. 爬虫请遵守网站的robots.txt规则
3. 建议设置合理的爬取频率，避免对目标网站造成压力
4. 定期检查日志文件，确保系统正常运行

## 常见问题

### Q: 如何修改爬取频率？
A: 编辑 `config/config.yaml` 中的 `schedule.cron` 字段

### Q: 如何添加新的文章分类？
A: 编辑 `config/categories.yaml`，添加新的分类配置

### Q: 如何查看爬取日志？
A: 查看 `logs/crawler.log` 文件

### Q: 如何手动触发爬取？
A: 运行 `python scripts/workflow.py`

## 贡献指南

欢迎提交Issue和Pull Request！

## 许可证

MIT License
