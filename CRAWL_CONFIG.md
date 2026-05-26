# 爬取内容配置指南

## 修改爬取的网站分类

编辑 `config/config.yaml` 文件中的 `categories` 配置：

```yaml
crawler:
  base_url: "https://www.woshipm.com"
  categories:
    - "pd"           # 产品设计
    - "it"           # 信息技术
    - "ai"           # 人工智能
    - "share"        # 分享
    - "class"        # 课堂
```

## 可用的分类

人人都是产品经理网站的分类：

| 分类代码 | 分类名称 | URL示例 |
|---------|---------|---------|
| `pd` | 产品设计 | https://www.woshipm.com/category/pd |
| `it` | 信息技术 | https://www.woshipm.com/category/it |
| `ai` | 人工智能 | https://www.woshipm.com/category/ai |
| `share` | 分享 | https://www.woshipm.com/category/share |
| `class` | 课堂 | https://www.woshipm.com/category/class |
| `operate` | 运营 | https://www.woshipm.com/category/operate |
| `ued` | 用户体验 | https://www.woshipm.com/category/ued |
| `dajiang` | 大讲堂 | https://www.woshipm.com/category/dajiang |
| `weidian` | 微店 | https://www.woshipm.com/category/weidian |
| `pmdis` | 产品讨论 | https://www.woshipm.com/category/pmdis |

## 修改爬取数量

```yaml
crawler:
  max_pages: 5  # 修改这个数字，每个分类爬取的页面数
```

- `1` - 爬取约20-30篇文章
- `5` - 爬取约100-150篇文章（默认）
- `10` - 爬取约200-300篇文章

## 修改爬取速度

```yaml
crawler:
  delay_seconds: 2  # 请求间隔（秒）
  timeout: 30       # 请求超时（秒）
  retry_times: 3    # 重试次数
```

- `delay_seconds`: 增大可避免被封禁，但速度变慢
- `timeout`: 增大可等待慢速响应
- `retry_times`: 增大可提高成功率

## 完整配置示例

### 示例1：只爬取产品设计和AI

```yaml
crawler:
  base_url: "https://www.woshipm.com"
  categories:
    - "pd"           # 产品设计
    - "ai"           # 人工智能
  max_pages: 3
  delay_seconds: 3
```

### 示例2：爬取所有分类

```yaml
crawler:
  base_url: "https://www.woshipm.com"
  categories:
    - "pd"
    - "it"
    - "ai"
    - "share"
    - "class"
    - "operate"
    - "ued"
    - "dajiang"
  max_pages: 10
  delay_seconds: 2
```

### 示例3：慢速爬取（避免被封）

```yaml
crawler:
  base_url: "https://www.woshipm.com"
  categories:
    - "pd"
  max_pages: 2
  delay_seconds: 5
  timeout: 60
  retry_times: 5
```

## 修改后运行

```bash
# 测试配置
python scripts/crawler.py --max-pages 1

# 运行完整工作流
python scripts/workflow.py

# 查看爬取结果
python scripts/workflow.py --mode status
```

## 查看爬取的文章

```bash
# 查看原始数据
ls data/raw/

# 查看今天的爬取
ls data/raw/$(date +%Y-%m-%d)/

# 查看知识库
ls knowledge_base/
```

## 添加新的网站源

如果要爬取其他网站，需要修改 `scripts/crawler.py`：

1. 修改 `crawl_article_list()` 方法的URL格式
2. 修改 `_parse_article_links()` 方法的解析逻辑
3. 修改 `crawl_article_detail()` 方法的详情解析

示例：
```python
def crawl_article_list(self, category: str, page: int = 1) -> List[Dict]:
    # 修改这里的URL格式
    url = f"https://其他网站.com/category/{category}?page={page}"
    # ...
```

## 常见问题

### Q: 如何查看哪些分类可用？
A: 访问 https://www.woshipm.com/ 查看导航栏

### Q: 爬取被封禁怎么办？
A: 增加 `delay_seconds` 到 5-10 秒

### Q: 如何只爬取最新文章？
A: 减少 `max_pages` 到 1-2

### Q: 如何爬取历史文章？
A: 增加 `max_pages` 到 10-20

### Q: 爬取速度太慢怎么办？
A: 减少 `delay_seconds` 到 1-2 秒（可能被封）
