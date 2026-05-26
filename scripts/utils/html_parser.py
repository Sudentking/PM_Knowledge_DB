"""HTML解析工具模块"""

import re
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from datetime import datetime

class ArticleParser:
    """文章解析器"""

    def __init__(self, html: str):
        """初始化解析器

        Args:
            html: HTML内容
        """
        self.soup = BeautifulSoup(html, 'lxml')

    def parse_article_list(self) -> List[Dict]:
        """解析文章列表

        Returns:
            文章列表，每个文章包含：id, title, url, summary, author, publish_time
        """
        articles = []

        # 查找文章列表容器
        # 注意：这里的选择器需要根据实际网站结构调整
        article_items = self.soup.select('div.post-list-item, article.post, div.article-item')

        for item in article_items:
            try:
                article = self._parse_article_item(item)
                if article:
                    articles.append(article)
            except Exception as e:
                continue

        return articles

    def _parse_article_item(self, item) -> Optional[Dict]:
        """解析单个文章项

        Args:
            item: 文章HTML元素

        Returns:
            文章信息字典
        """
        # 提取标题和链接
        title_elem = item.select_one('h2 a, h3 a, .post-title a, .article-title a')
        if not title_elem:
            return None

        title = title_elem.get_text(strip=True)
        url = title_elem.get('href', '')

        # 确保URL是完整的
        if url and not url.startswith('http'):
            url = 'https://www.woshipm.com' + url

        # 从URL中提取文章ID
        article_id = self._extract_article_id(url)

        # 提取摘要
        summary_elem = item.select_one('.post-excerpt, .article-summary, .post-content p')
        summary = summary_elem.get_text(strip=True) if summary_elem else ''

        # 提取作者
        author_elem = item.select_one('.post-author, .article-author, .author-name')
        author = author_elem.get_text(strip=True) if author_elem else ''

        # 提取发布时间
        time_elem = item.select_one('.post-date, .article-time, time')
        publish_time = time_elem.get_text(strip=True) if time_elem else ''

        # 提取分类
        category_elem = item.select_one('.post-category, .article-category, .category-tag')
        category = category_elem.get_text(strip=True) if category_elem else ''

        return {
            'id': article_id,
            'title': title,
            'url': url,
            'summary': summary,
            'author': author,
            'publish_time': publish_time,
            'category': category,
            'crawled_at': datetime.now().isoformat()
        }

    def parse_article_detail(self) -> Dict:
        """解析文章详情

        Returns:
            文章详情，包含：title, content, author, publish_time, tags
        """
        # 提取标题 - 尝试多种选择器
        title = ''
        title_selectors = [
            'h1.post-title',
            'h1.article-title',
            '.article-header h1',
            '.post-title',
            '.article-title',
            'h1'
        ]
        for selector in title_selectors:
            title_elem = self.soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                if title:
                    break

        # 如果还是没有标题，从title标签提取
        if not title:
            title_elem = self.soup.select_one('title')
            if title_elem:
                title = title_elem.get_text(strip=True)
                # 移除网站名称
                if ' | ' in title:
                    title = title.split(' | ')[0]

        # 提取内容
        content_elem = self.soup.select_one('.post-content, .article-content, .entry-content, .article-detail')
        content = ''
        if content_elem:
            # 移除脚本和样式标签
            for script in content_elem(['script', 'style']):
                script.decompose()
            content = content_elem.get_text(separator='\n', strip=True)

        # 提取作者 - 尝试多种选择器
        author = ''
        author_selectors = [
            '.post-author',
            '.article-author',
            '.author-name',
            '.author',
            '.writer',
            '.user-name'
        ]
        for selector in author_selectors:
            author_elem = self.soup.select_one(selector)
            if author_elem:
                author = author_elem.get_text(strip=True)
                if author:
                    break

        # 提取发布时间
        publish_time = ''
        time_selectors = [
            '.post-date',
            '.article-time',
            'time',
            '.date',
            '.time',
            '.publish-time'
        ]
        for selector in time_selectors:
            time_elem = self.soup.select_one(selector)
            if time_elem:
                publish_time = time_elem.get_text(strip=True)
                if publish_time:
                    break

        # 提取标签
        tags = []
        tag_selectors = [
            '.post-tag',
            '.article-tag',
            '.tag-item',
            '.tag',
            '.label'
        ]
        for selector in tag_selectors:
            tag_elems = self.soup.select(selector)
            for tag_elem in tag_elems:
                tag = tag_elem.get_text(strip=True)
                if tag and tag not in tags:
                    tags.append(tag)

        # 提取正文HTML（保留格式）
        content_html = ''
        if content_elem:
            content_html = str(content_elem)

        return {
            'title': title,
            'content': content,
            'content_html': content_html,
            'author': author,
            'publish_time': publish_time,
            'tags': tags,
            'parsed_at': datetime.now().isoformat()
        }

    def _extract_article_id(self, url: str) -> str:
        """从URL中提取文章ID

        Args:
            url: 文章URL

        Returns:
            文章ID
        """
        # 尝试从URL中提取数字ID
        match = re.search(r'/(\d+)\.html', url)
        if match:
            return match.group(1)

        # 如果没有找到，使用URL的hash作为ID
        import hashlib
        return hashlib.md5(url.encode()).hexdigest()[:12]

    def get_pagination_links(self) -> List[str]:
        """获取分页链接

        Returns:
            分页URL列表
        """
        pagination_links = []

        # 查找分页容器
        pagination = self.soup.select_one('.pagination, .page-nav, .pager')
        if pagination:
            links = pagination.select('a')
            for link in links:
                href = link.get('href', '')
                if href and not href.startswith('http'):
                    href = 'https://www.woshipm.com' + href
                if href and href not in pagination_links:
                    pagination_links.append(href)

        return pagination_links


class ContentCleaner:
    """内容清洗器"""

    @staticmethod
    def clean_text(text: str) -> str:
        """清洗文本内容

        Args:
            text: 原始文本

        Returns:
            清洗后的文本
        """
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        # 移除特殊字符
        text = re.sub(r'[^\w\s一-龥，。！？、；：""''（）【】]', '', text)
        # 去除首尾空白
        text = text.strip()
        return text

    @staticmethod
    def extract_keywords(text: str, top_n: int = 10) -> List[str]:
        """提取关键词（简单实现）

        Args:
            text: 文本内容
            top_n: 返回前N个关键词

        Returns:
            关键词列表
        """
        # 简单的基于词频的关键词提取
        # 实际项目中可以使用jieba等分词工具
        words = re.findall(r'[一-龥]{2,}', text)
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # 按频率排序
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:top_n]]
