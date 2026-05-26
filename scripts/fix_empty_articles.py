"""修复空文章脚本 - 重新爬取和总结失败的文章"""

import os
import sys
import json
import time
from pathlib import Path

import yaml
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.utils.logger import setup_logger

def find_empty_articles():
    """找到所有内容为空的文章"""
    kb_dir = Path("knowledge_base")
    empty_articles = []

    for root, dirs, files in os.walk(kb_dir):
        for f in files:
            if '_待补充_' in f:
                path = os.path.join(root, f)
                # 提取文章ID
                article_id = f.split('_待补充_')[1].replace('.md', '')
                # 提取分类
                parts = root.split(os.sep)
                category = parts[-2] if len(parts) > 1 else 'unknown'
                empty_articles.append({
                    'id': article_id,
                    'category': category,
                    'path': path,
                    'filename': f
                })

    return empty_articles

def crawl_article(article_id, category, config):
    """爬取单个文章"""
    base_url = config.get('crawler', {}).get('base_url', 'https://www.woshipm.com')

    # 分类映射（反向）
    category_map = {
        'ai': 'ai',
        'class': 'class',
        'it': 'it',
        'product-design': 'pd',
        'share': 'share'
    }

    raw_category = category_map.get(category, category)
    url = f"{base_url}/{raw_category}/{article_id}.html"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')

            # 提取标题
            title = ''
            for selector in ['h1.post-title', 'h1.article-title', '.article-header h1', 'h1']:
                elem = soup.select_one(selector)
                if elem:
                    title = elem.get_text(strip=True)
                    if title:
                        break

            if not title:
                title_elem = soup.select_one('title')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if ' | ' in title:
                        title = title.split(' | ')[0]

            # 提取内容
            content_elem = soup.select_one('.article--content, .post-content, .article-content, .entry-content, .article-detail')
            content = ''
            if content_elem:
                for script in content_elem(['script', 'style']):
                    script.decompose()
                content = content_elem.get_text(separator='\n', strip=True)

            # 提取作者
            author = ''
            for selector in ['.post-author', '.article-author', '.author-name', '.author']:
                elem = soup.select_one(selector)
                if elem:
                    author = elem.get_text(strip=True)
                    if author:
                        break

            return {
                'id': article_id,
                'title': title,
                'content': content,
                'author': author,
                'url': url,
                'category': category,
                'status': 'success' if content else 'empty_content'
            }
        else:
            return {'id': article_id, 'status': f'http_{response.status_code}'}
    except Exception as e:
        return {'id': article_id, 'status': f'error: {str(e)}'}

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='修复空文章')
    parser.add_argument('--limit', type=int, default=10, help='最多处理的文章数量')
    parser.add_argument('--dry-run', action='store_true', help='仅显示要处理的文章')

    args = parser.parse_args()

    # 加载配置
    with open('config/config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # 初始化日志
    logger = setup_logger(
        config.get('logging', {}).get('file', 'logs/crawler.log'),
        config.get('logging', {}).get('level', 'INFO')
    )

    # 找到空文章
    empty_articles = find_empty_articles()
    print(f"找到 {len(empty_articles)} 篇空文章")

    if args.dry_run:
        for article in empty_articles[:args.limit]:
            print(f"  - {article['filename']} ({article['category']})")
        return

    # 处理文章
    fixed = 0
    for article in empty_articles[:args.limit]:
        print(f"\n处理: {article['id']} ({article['category']})")

        # 爬取文章
        result = crawl_article(article['id'], article['category'], config)

        if result.get('status') == 'success' and result.get('content'):
            # 保存原始数据
            raw_dir = Path("data/raw/2026-05-26")
            raw_dir.mkdir(parents=True, exist_ok=True)
            raw_file = raw_dir / f"{article['id']}.json"
            with open(raw_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            # AI总结
            try:
                from openai import OpenAI

                client = OpenAI(
                    api_key=os.environ.get('DEEPSEEK_API_KEY'),
                    base_url=os.environ.get('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
                )

                content = result.get('content', '')[:3000]
                prompt = f"""请用200-300字总结这篇文章的核心观点：

{content}

要求：直接输出总结内容，不要说"好的"或"以下是"等开场白。"""

                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.3
                )
                summary = response.choices[0].message.content

                # 更新知识库文件
                title = result.get('title', '') or f"文章_{article['id']}"
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
                if not safe_title:
                    safe_title = f"{article['category']}_{article['id']}"

                # 生成Markdown
                markdown = f"""# {title}

**作者**: {result.get('author', '')}
**发布时间**: 2026-05-26
**原文链接**: [{result['url']}]({result['url']})
**分类**: {article['category']}

---

{summary}

---

*本文由AI自动总结生成，仅供参考。*
"""

                # 删除旧文件，创建新文件
                old_path = Path(article['path'])
                new_path = old_path.parent / f"{safe_title}.md"

                if new_path.exists():
                    new_path = old_path.parent / f"{safe_title}_{article['id']}.md"

                old_path.unlink()
                with open(new_path, 'w', encoding='utf-8') as f:
                    f.write(markdown)

                print(f"  OK: {safe_title}.md")
                fixed += 1

            except Exception as e:
                print(f"  总结失败: {e}")
        else:
            print(f"  爬取失败: {result.get('status', 'unknown')}")

        # 限速
        time.sleep(2)

    print(f"\n完成: 修复了 {fixed}/{min(len(empty_articles), args.limit)} 篇文章")

if __name__ == "__main__":
    main()
