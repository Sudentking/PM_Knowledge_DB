"""AI总结模块"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

import yaml
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.utils.logger import setup_logger, get_logger

class ArticleSummarizer:
    """文章总结器"""

    def __init__(self, config_path: str = "config/config.yaml"):
        """初始化总结器

        Args:
            config_path: 配置文件路径
        """
        # 加载配置
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        # 初始化日志
        self.logger = setup_logger(
            self.config.get('logging', {}).get('file', 'logs/crawler.log'),
            self.config.get('logging', {}).get('level', 'INFO')
        )

        # AI配置
        ai_config = self.config.get('summarizer', {})
        self.provider = ai_config.get('provider', 'deepseek')
        self.api_key = os.environ.get('DEEPSEEK_API_KEY') or ai_config.get('api_key', '')
        self.base_url = os.environ.get('DEEPSEEK_BASE_URL') or ai_config.get('base_url', 'https://api.deepseek.com')
        self.model = ai_config.get('model', 'deepseek-chat')
        self.max_tokens = ai_config.get('max_tokens', 1500)
        self.temperature = ai_config.get('temperature', 0.3)

        # 初始化AI客户端
        self.client = None
        self._init_ai_client()

        # 数据目录
        self.raw_dir = Path("data/raw")
        self.processed_dir = Path("data/processed")
        self.processed_dir.mkdir(parents=True, exist_ok=True)

        # 索引文件
        self.index_file = Path("data/index.json")
        self.index = self._load_index()

    def _init_ai_client(self):
        """初始化AI客户端"""
        if self.provider in ['openai', 'deepseek']:
            try:
                import openai
                self.client = openai.OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
                self.logger.info(f"已初始化{self.provider.upper()}客户端")
            except ImportError:
                self.logger.error("未安装openai库，请运行: pip install openai")
            except Exception as e:
                self.logger.error(f"初始化{self.provider.upper()}客户端失败: {e}")

        elif self.provider == 'claude':
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
                self.logger.info("已初始化Claude客户端")
            except ImportError:
                self.logger.error("未安装anthropic库，请运行: pip install anthropic")
            except Exception as e:
                self.logger.error(f"初始化Claude客户端失败: {e}")

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

    def _build_prompt(self, article: Dict) -> str:
        """构建提示词

        Args:
            article: 文章数据

        Returns:
            提示词
        """
        title = article.get('title', '')
        content = article.get('content', '')
        author = article.get('author', '')

        prompt = f"""请对以下产品经理相关文章进行详细总结，字数要求800-1000字。

文章标题：{title}
文章作者：{author}

文章内容：
{content[:3000]}

请按照以下格式进行总结：

## 核心观点（200字）
总结文章的核心论点和主要观点

## 方法论/框架（300字）
提取文章中提到的方法论、框架、模型或工具

## 关键案例（200字）
总结文章中的关键案例和实证

## 实践建议（200字）
提取文章中的实践建议和行动指南

## 关键词标签
提取5-8个关键词，用逗号分隔

请确保总结内容：
1. 准确反映原文观点
2. 保留具体的方法和步骤
3. 突出实用性和可操作性
4. 使用清晰的结构和标题
"""
        return prompt

    def _call_openai(self, prompt: str) -> Optional[str]:
        """调用OpenAI API

        Args:
            prompt: 提示词

        Returns:
            生成的内容
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的产品经理知识总结专家，擅长提取文章的核心观点和方法论。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"调用OpenAI API失败: {e}")
            return None

    def _call_claude(self, prompt: str) -> Optional[str]:
        """调用Claude API

        Args:
            prompt: 提示词

        Returns:
            生成的内容
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            self.logger.error(f"调用Claude API失败: {e}")
            return None

    def summarize_article(self, article: Dict) -> Optional[str]:
        """总结文章

        Args:
            article: 文章数据

        Returns:
            总结内容
        """
        if not self.client:
            self.logger.error("AI客户端未初始化")
            return None

        prompt = self._build_prompt(article)

        if self.provider in ['openai', 'deepseek']:
            return self._call_openai(prompt)
        elif self.provider == 'claude':
            return self._call_claude(prompt)
        else:
            self.logger.error(f"不支持的AI提供商: {self.provider}")
            return None

    def save_summary(self, article_id: str, article: Dict, summary: str):
        """保存总结

        Args:
            article_id: 文章ID
            article: 文章数据
            summary: 总结内容
        """
        today = datetime.now().strftime("%Y-%m-%d")

        # 保存到processed目录
        processed_dir = self.processed_dir / today
        processed_dir.mkdir(parents=True, exist_ok=True)

        summary_data = {
            'id': article_id,
            'title': article.get('title', ''),
            'author': article.get('author', ''),
            'url': article.get('url', ''),
            'category': article.get('category', ''),
            'summary': summary,
            'summarized_at': datetime.now().isoformat()
        }

        file_path = processed_dir / f"{article_id}_summary.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)

        self.logger.info(f"已保存总结: {file_path}")

    def generate_markdown(self, article_id: str, article: Dict, summary: str) -> str:
        """生成Markdown格式的知识库文章

        Args:
            article_id: 文章ID
            article: 文章数据
            summary: 总结内容

        Returns:
            Markdown内容
        """
        title = article.get('title', '')
        author = article.get('author', '')
        url = article.get('url', '')
        publish_time = article.get('publish_time', '')
        tags = article.get('tags', [])

        markdown = f"""# {title}

**作者**: {author}
**发布时间**: {publish_time}
**原文链接**: [{url}]({url})
**标签**: {', '.join(tags)}

---

{summary}

---

*本文由AI自动总结生成，仅供参考。*
"""
        return markdown

    def save_to_knowledge_base(self, article_id: str, article: Dict, summary: str):
        """保存到知识库

        Args:
            article_id: 文章ID
            article: 文章数据
            summary: 总结内容
        """
        category = article.get('category', 'uncategorized')
        today = datetime.now().strftime("%Y-%m-%d")

        # 确定知识库目录
        # 这里简单处理，实际项目中需要根据分类配置映射
        category_mapping = {
            'pd': 'product-design',
            'user-research': 'user-research',
            'data-analysis': 'data-analysis',
            'project-management': 'project-management',
            'strategy': 'strategy',
            'industry-insights': 'industry-insights'
        }
        kb_category = category_mapping.get(category, 'uncategorized')

        # 创建目录
        kb_dir = Path(f"knowledge_base/{kb_category}/{today}")
        kb_dir.mkdir(parents=True, exist_ok=True)

        # 生成Markdown
        markdown = self.generate_markdown(article_id, article, summary)

        # 保存文件
        title = article.get('title', 'untitled')
        # 清理文件名
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
        file_path = kb_dir / f"{safe_title}.md"

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown)

        self.logger.info(f"已保存到知识库: {file_path}")

    def process_article(self, article_id: str) -> bool:
        """处理单篇文章

        Args:
            article_id: 文章ID

        Returns:
            是否成功
        """
        # 检查是否已总结
        if self.index.get('articles', {}).get(article_id, {}).get('summarized', False):
            self.logger.info(f"文章已总结，跳过: {article_id}")
            return True

        # 加载原始文章
        raw_file = self._find_raw_file(article_id)
        if not raw_file:
            self.logger.error(f"找不到原始文章文件: {article_id}")
            return False

        with open(raw_file, 'r', encoding='utf-8') as f:
            article = json.load(f)

        # 生成总结
        self.logger.info(f"正在总结文章: {article.get('title', '')}")
        summary = self.summarize_article(article)

        if not summary:
            self.logger.error(f"总结文章失败: {article_id}")
            return False

        # 保存总结
        self.save_summary(article_id, article, summary)

        # 保存到知识库
        self.save_to_knowledge_base(article_id, article, summary)

        # 更新索引
        if article_id in self.index.get('articles', {}):
            self.index['articles'][article_id]['summarized'] = True
            self._save_index()

        return True

    def _find_raw_file(self, article_id: str) -> Optional[Path]:
        """查找原始文章文件

        Args:
            article_id: 文章ID

        Returns:
            文件路径
        """
        # 在raw目录中查找
        for date_dir in self.raw_dir.iterdir():
            if date_dir.is_dir():
                file_path = date_dir / f"{article_id}.json"
                if file_path.exists():
                    return file_path
        return None

    def process_all(self) -> int:
        """处理所有未总结的文章

        Returns:
            处理的文章数量
        """
        processed_count = 0

        # 遍历raw目录
        for date_dir in self.raw_dir.iterdir():
            if not date_dir.is_dir():
                continue

            for file_path in date_dir.glob("*.json"):
                article_id = file_path.stem

                if self.process_article(article_id):
                    processed_count += 1

        self.logger.info(f"共处理 {processed_count} 篇文章")
        return processed_count

    def process_today(self) -> int:
        """处理今天爬取的文章

        Returns:
            处理的文章数量
        """
        today = datetime.now().strftime("%Y-%m-%d")
        today_dir = self.raw_dir / today

        if not today_dir.exists():
            self.logger.info(f"今天没有爬取数据: {today}")
            return 0

        processed_count = 0
        for file_path in today_dir.glob("*.json"):
            article_id = file_path.stem

            if self.process_article(article_id):
                processed_count += 1

        self.logger.info(f"今天共处理 {processed_count} 篇文章")
        return processed_count


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='文章AI总结工具')
    parser.add_argument('--config', default='config/config.yaml', help='配置文件路径')
    parser.add_argument('--article-id', help='指定处理的文章ID')
    parser.add_argument('--today', action='store_true', help='只处理今天的文章')
    parser.add_argument('--all', action='store_true', help='处理所有未总结的文章')

    args = parser.parse_args()

    # 创建总结器实例
    summarizer = ArticleSummarizer(args.config)

    # 执行总结
    if args.article_id:
        success = summarizer.process_article(args.article_id)
        print(f"处理文章 {'成功' if success else '失败'}: {args.article_id}")
    elif args.today:
        count = summarizer.process_today()
        print(f"今天共处理 {count} 篇文章")
    elif args.all:
        count = summarizer.process_all()
        print(f"共处理 {count} 篇文章")
    else:
        # 默认处理今天的文章
        count = summarizer.process_today()
        print(f"今天共处理 {count} 篇文章")


if __name__ == "__main__":
    main()
