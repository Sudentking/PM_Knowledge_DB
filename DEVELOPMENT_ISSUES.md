# 开发问题总结文档

> 本文档记录开发过程中遇到的问题和解决方案，供后续维护和AI迁移参考。

**项目名称**: 产品经理知识库 (PM_Knowledge_DB)
**创建时间**: 2026-05-26
**当前版本**: v1.1.0

---

## 版本记录

| 版本 | 日期 | 主要变更 |
|------|------|----------|
| v1.1.0 | 2026-05-27 | 完善文章命名方法，集成到工作流，添加去重逻辑 |
| v1.0.0 | 2026-05-26 | 初始版本，完成爬虫+总结+知识库全流程 |

---

## 问题1: Windows GBK编码错误

**时间**: 2026-05-26
**错误现象**:
```
UnicodeEncodeError: 'gbk' codec can't encode character '✓' in position 0
```

**原因**: Windows默认终端使用GBK编码，无法显示Unicode特殊字符（如 ✓、✗、→）

**解决方案**:
```python
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

**教训**:
- Windows环境下输出包含特殊字符时，必须设置UTF-8编码
- 避免在print语句中使用Unicode特殊符号，改用ASCII替代（如 [OK]、[FAIL]）

---

## 问题2: woshipm.com URL格式错误

**时间**: 2026-05-26
**错误现象**: 爬虫返回0篇文章，URL格式 `/category/{category}/page/{page}` 无法访问

**原因**: woshipm.com的实际URL结构与预期不同

**实际URL结构**:
- 分类页: `https://www.woshipm.com/pd` (无 `/category/` 前缀)
- 文章页: `https://www.woshipm.com/pd/6206871.html`
- 分页: `https://www.woshipm.com/pd/page/2`

**解决方案**:
```python
# 错误的URL格式
url = f"{base_url}/category/{category}/page/{page}"

# 正确的URL格式
url = f"{base_url}/{category}/page/{page}"
```

**教训**:
- 爬虫开发前必须手动访问目标网站，确认实际URL结构
- 不要假设URL格式，要通过浏览器开发者工具验证

---

## 问题3: Git分支名称不匹配

**时间**: 2026-05-26
**错误现象**: `git push` 失败，提示分支不存在

**原因**: config.yaml中配置了 `branch: "main"`，但本地仓库使用 `master`

**解决方案**:
```yaml
# config/config.yaml
git:
  branch: "master"  # 改为实际使用的分支名
```

**教训**:
- 初始化Git仓库后，先用 `git branch` 确认当前分支名
- GitHub新建仓库默认分支可能是 `main` 或 `master`，需统一

---

## 问题4: Git Push认证失败

**时间**: 2026-05-26
**错误现象**:
```
fatal: could not read Username for 'https://github.com': No such file or directory
```

**原因**: Git在非交互式环境中无法弹出认证窗口

**解决方案**: 使用Personal Access Token (PAT)嵌入远程URL
```bash
# 设置带token的远程地址
git remote set-url origin https://{TOKEN}@github.com/username/repo.git
```

**教训**:
- 自动化脚本中不能依赖交互式认证
- PAT需要在GitHub Settings > Developer settings > Personal access tokens中生成
- PAT权限要包含 `repo` 读写权限

---

## 问题5: 文章标题提取失败

**时间**: 2026-05-26
**错误现象**: 爬取的文章标题为空，导致文件名变成 `.md` 或 `文章_ID.md`

**原因**: woshipm.com文章页的标题选择器不统一，部分页面没有预期的HTML结构

**解决方案**:
1. 增加多种CSS选择器:
```python
title_selectors = [
    'h1.post-title',
    'h1.article-title',
    '.article-header h1',
    '.post-title',
    '.article-title',
    'h1'
]
```

2. 添加 `<title>` 标签回退:
```python
if not title:
    title_elem = self.soup.select_one('title')
    if title_elem:
        title = title_elem.get_text(strip=True)
        if ' | ' in title:
            title = title.split(' | ')[0]
```

**教训**:
- 网页解析不能依赖单一选择器
- 必须有回退机制（如从 `<title>` 标签提取）
- 首次爬取时应保存原始HTML，便于后续调试

---

## 问题6: 知识库文件名为空

**时间**: 2026-05-26
**错误现象**: knowledge_base目录下出现 `.md` 文件（文件名为空）

**原因**: 标题提取失败后，`generate_safe_filename("")` 返回空字符串

**解决方案**:
```python
safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
if not safe_title:
    safe_title = f"article_{article_id}"  # 使用ID作为回退
```

**教训**:
- 文件名生成必须有默认值
- 清理非法字符后要检查是否为空

---

## 问题7: DeepSeek API配置

**时间**: 2026-05-26
**注意事项**: DeepSeek API兼容OpenAI格式，但需要自定义base_url

**正确配置**:
```python
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"  # 必须指定
)
```

**config.yaml配置**:
```yaml
summarizer:
  provider: "deepseek"
  api_key: "${DEEPSEEK_API_KEY}"
  base_url: "${DEEPSEEK_BASE_URL}"
  model: "deepseek-chat"
```

**.env文件**:
```
DEEPSEEK_API_KEY=sk-xxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

**教训**:
- DeepSeek是OpenAI兼容API，可以用openai库调用
- 但必须指定 `base_url`，否则默认请求OpenAI地址
- API Key不要硬编码，使用环境变量

---

## 问题8: Windows路径分隔符

**时间**: 2026-05-26
**错误现象**: 某些情况下路径拼接错误

**解决方案**: 使用 `pathlib.Path` 替代字符串拼接
```python
from pathlib import Path

# 错误方式
path = "data/raw" + "/" + date + "/" + filename

# 正确方式
path = Path("data/raw") / date / filename
```

**教训**:
- 始终使用 `pathlib` 处理路径，避免手动拼接
- Windows和Linux路径分隔符不同，`pathlib` 会自动处理

---

## 问题9: 限速和反爬

**时间**: 2026-05-26
**注意事项**: 爬虫需要控制速度，避免被封IP

**建议配置**:
```yaml
crawler:
  delay_seconds: 2  # 每次请求间隔2秒
```

**代码实现**:
```python
import time
import random

# 随机延迟，更像人类行为
time.sleep(self.delay + random.uniform(0, 1))
```

**教训**:
- 爬虫必须有延迟，不要高频请求
- 使用随机延迟更自然
- 设置合理的User-Agent

---

## 问题10: 文件编码问题

**时间**: 2026-05-26
**错误现象**: 中文内容保存后乱码

**解决方案**: 所有文件操作指定UTF-8编码
```python
# 读取
with open(file, 'r', encoding='utf-8') as f:
    content = f.read()

# 写入
with open(file, 'w', encoding='utf-8') as f:
    f.write(content)
```

**教训**:
- Python在Windows上默认使用系统编码（GBK）
- 处理中文内容必须显式指定 `encoding='utf-8'`

---

## 问题11: 文章标题提取失败

**时间**: 2026-05-27
**错误现象**: 爬取的文章标题为空，导致文件名变成 `文章_ID.md` 或 `.md`

**原因**:
1. 网页标题选择器不统一
2. 部分文章内容为空（爬取失败）
3. AI总结内容格式不统一

**解决方案 - 多层级标题提取策略**:

```python
def extract_title(content, raw_data, summary):
    """多层级标题提取"""
    title = ""

    # 方法1: 从文件第一行提取（# 标题格式）
    first_line = content.split('\n')[0].strip()
    if first_line.startswith('#'):
        title = first_line.lstrip('#').strip()

    # 方法2: 从原始数据中提取
    if not title and raw_data:
        title = raw_data.get('title', '')

    # 方法3: 从AI总结的"核心观点"中提取主题
    if not title:
        # 匹配 "核心观点是：xxx" 或 "核心思想是xxx"
        match = re.search(r'(?:核心观点|核心思想)[是为：:\s]+(.+?)(?:[。,.]|$)', summary)
        if match:
            title = match.group(1).strip()[:50]

    # 方法4: 使用分类+ID作为兜底
    if not title:
        title = f"{category}_待补充_{article_id}"

    return title
```

**已集成到工作流**: `workflow.py` 的 `_rename_articles()` 方法会自动在总结完成后重命名文章

---

## 问题12: 文章内容为空

**时间**: 2026-05-27
**错误现象**: AI总结返回"请提供文章内容"，实际是爬虫未获取到内容

**原因**: woshipm.com的内容容器选择器是 `.article--content`，而非通用的 `.post-content`

**解决方案**: 使用正确的选择器
```python
content_elem = soup.select_one('.article--content, .post-content, .article-content')
```

**修复脚本**: `scripts/fix_empty_articles.py` 可以重新爬取和总结失败的文章

---

## 问题13: 文章去重机制

**时间**: 2026-05-27
**需求**: 避免重复爬取已存在的文章

**实现方案**:
1. 使用 `data/index.json` 记录所有已爬取的文章ID
2. 爬取前检查文章ID是否已存在
3. workflow.py 的 `_get_existing_article_ids()` 方法加载已有文章

```python
def is_article_crawled(self, article_id: str) -> bool:
    return article_id in self.index.get('articles', {})
```

**去重逻辑已集成到**:
- `crawler.py`: 爬取时自动跳过已存在的文章
- `workflow.py`: 运行前加载已有文章ID列表

---

## 常见坑总结

### 1. 编码问题
- Windows默认GBK，Python默认系统编码
- **规则**: 所有文件操作加 `encoding='utf-8'`

### 2. 路径问题
- Windows用 `\`，Linux用 `/`
- **规则**: 使用 `pathlib.Path`

### 3. 网页解析
- 网站结构可能变化
- **规则**: 多选择器 + 回退机制

### 4. API配置
- 不同AI服务有不同的base_url
- **规则**: 使用环境变量，不硬编码

### 5. Git认证
- 自动化脚本不能用交互式认证
- **规则**: 使用Personal Access Token

### 6. 错误处理
- 爬虫要能容忍单个失败
- **规则**: try-except包裹，记录日志继续

---

## 迁移检查清单

当更换AI服务或迁移环境时，检查以下内容:

- [ ] `.env` 文件中的API Key是否正确
- [ ] `config.yaml` 中的provider和base_url是否匹配
- [ ] Git remote URL中的token是否有效
- [ ] Python依赖是否安装 (`pip install -r requirements.txt`)
- [ ] 定时任务是否配置
- [ ] 日志目录是否存在

---

## 联系方式

如有问题，请查看：
- GitHub Issues: https://github.com/Sudentking/PM_Knowledge_DB/issues
- 项目文档: README.md
