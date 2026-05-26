"""爬虫主模块"""

import os
import sys
import json
import time
import random
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.utils.logger import setup_logger, get_logger
from scripts.utils.html_parser import ArticleParser, ContentCleaner

class WoshipmCrawler:
    """人人都是产品经理网站爬虫"""

    def __init__(self, config_path: str = "config/config.yaml"):
        """初始化爬虫

        Args:
            config_path: 配置文件路径
        """
        import yaml

        # 加载配置
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        # 初始化日志
        self.logger = setup_logger(
            self.config.get('logging', {}).get('file', 'logs/crawler.log'),
            self.config.get('logging', {}).get('level', 'INFO')
        )

        # 爬虫配置
        crawler_config = self.config.get('crawler', {})
        self.base_url = crawler_config.get('base_url', 'https://www.woshipm.com')
        self.categories = crawler_config.get('categories', ['pd'])
        self.max_pages = crawler_config.get('max_pages', 5)
        self.delay_seconds = crawler_config.get('delay_seconds', 2)
        self.timeout = crawler_config.get('timeout', 30)
        self.retry_times = crawler_config.get('retry_times', 3)

        # 初始化会话
        self.session = requests.Session()
        self.ua = UserAgent()

        # 数据目录
        self.data_dir = Path("data/raw")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 索引文件
        self.index_file = Path("data/index.json")
        self.index = self._load_index()

    def _load_index(self) -> Dict:
        """加载索引文件

        Returns:
            索引字典
        """
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'articles': {}, 'last_crawl': None}

    def _save_index(self):
        """保存索引文件"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)

    def _get_headers(self) -> Dict:
        """获取请求头

        Returns:
            请求头字典
        """
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def _request(self, url: str, method: str = 'GET', **kwargs) -> Optional[requests.Response]:
        """发送HTTP请求

        Args:
            url: 请求URL
            method: 请求方法
            **kwargs: 其他参数

        Returns:
            响应对象
        """
        for attempt in range(self.retry_times):
            try:
                headers = self._get_headers()
                response = self.session.request(
                    method,
                    url,
                    headers=headers,
                    timeout=self.timeout,
                    **kwargs
                )
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                self.logger.warning(f"请求失败 (尝试 {attempt + 1}/{self.retry_times}): {e}")
                if attempt < self.retry_times - 1:
                    time.sleep(random.uniform(1, 3))
        return None

    def crawl_article_list(self, category: str, page: int = 1) -> List[Dict]:
        """爬取文章列表

        Args:
            category: 文章分类
            page: 页码

        Returns:
            文章列表
        """
        # 构建URL
        # 注意：这里的URL格式需要根据实际网站结构调整
        url = f"{self.base_url}/category/{category}/page/{page}"

        self.logger.info(f"正在爬取文章列表: {url}")

        response = self._request(url)
        if not response:
            self.logger.error(f"无法访问: {url}")
            return []

        # 解析文章列表
        parser = ArticleParser(response.text)
        articles = parser.parse_article_list()

        self.logger.info(f"找到 {len(articles)} 篇文章")
        return articles

    def crawl_article_detail(self, url: str) -> Optional[Dict]:
        """爬取文章详情

        Args:
            url: 文章URL

        Returns:
            文章详情
        """
        self.logger.info(f"正在爬取文章详情: {url}")

        response = self._request(url)
        if not response:
            self.logger.error(f"无法访问: {url}")
            return None

        # 解析文章详情
        parser = ArticleParser(response.text)
        article = parser.parse_article_detail()

        return article

    def save_article(self, article_id: str, data: Dict, data_type: str = "raw"):
        """保存文章数据

        Args:
            article_id: 文章ID
            data: 文章数据
            data_type: 数据类型 (raw/processed)
        """
        today = datetime.now().strftime("%Y-%m-%d")
        save_dir = Path(f"data/{data_type}/{today}")
        save_dir.mkdir(parents=True, exist_ok=True)

        file_path = save_dir / f"{article_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self.logger.info(f"已保存文章: {file_path}")

    def is_article_crawled(self, article_id: str) -> bool:
        """检查文章是否已爬取

        Args:
            article_id: 文章ID

        Returns:
            是否已爬取
        """
        return article_id in self.index.get('articles', {})

    def add_to_index(self, article_id: str, article_info: Dict):
        """添加文章到索引

        Args:
            article_id: 文章ID
            article_info: 文章信息
        """
        if 'articles' not in self.index:
            self.index['articles'] = {}

        self.index['articles'][article_id] = {
            'title': article_info.get('title', ''),
            'url': article_info.get('url', ''),
            'category': article_info.get('category', ''),
            'crawled_at': datetime.now().isoformat(),
            'summarized': False
        }

        self._save_index()

    def crawl_category(self, category: str, max_pages: int = None) -> List[Dict]:
        """爬取指定分类的所有文章

        Args:
            category: 分类名称
            max_pages: 最大页数

        Returns:
            爬取的文章列表
        """
        if max_pages is None:
            max_pages = self.max_pages

        all_articles = []

        for page in range(1, max_pages + 1):
            self.logger.info(f"正在爬取 {category} 第 {page} 页")

            articles = self.crawl_article_list(category, page)

            if not articles:
                self.logger.info(f"第 {page} 页没有文章，停止爬取")
                break

            for article in articles:
                article_id = article.get('id')

                # 检查是否已爬取
                if self.is_article_crawled(article_id):
                    self.logger.info(f"文章已存在，跳过: {article_id}")
                    continue

                # 爬取文章详情
                detail = self.crawl_article_detail(article.get('url'))
                if detail:
                    # 合并信息
                    article_data = {**article, **detail}

                    # 保存文章
                    self.save_article(article_id, article_data, "raw")

                    # 添加到索引
                    self.add_to_index(article_id, article)

                    all_articles.append(article_data)

                # 随机延迟
                time.sleep(random.uniform(self.delay_seconds, self.delay_seconds + 2))

            # 页面间延迟
            time.sleep(random.uniform(3, 5))

        self.logger.info(f"共爬取 {len(all_articles)} 篇新文章")
        return all_articles

    def crawl_all(self) -> List[Dict]:
        """爬取所有分类的文章

        Returns:
            所有爬取的文章
        """
        all_articles = []

        for category in self.categories:
            self.logger.info(f"开始爬取分类: {category}")
            articles = self.crawl_category(category)
            all_articles.extend(articles)

        # 更新最后爬取时间
        self.index['last_crawl'] = datetime.now().isoformat()
        self._save_index()

        self.logger.info(f"爬取完成，共 {len(all_articles)} 篇新文章")
        return all_articles


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='人人都是产品经理网站爬虫')
    parser.add_argument('--config', default='config/config.yaml', help='配置文件路径')
    parser.add_argument('--category', help='指定爬取的分类')
    parser.add_argument('--max-pages', type=int, help='最大爬取页数')

    args = parser.parse_args()

    # 创建爬虫实例
    crawler = WoshipmCrawler(args.config)

    # 执行爬取
    if args.category:
        articles = crawler.crawl_category(args.category, args.max_pages)
    else:
        articles = crawler.crawl_all()

    print(f"爬取完成，共 {len(articles)} 篇新文章")


if __name__ == "__main__":
    main()
