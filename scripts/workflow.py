"""工作流编排模块"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, List
from pathlib import Path

import yaml

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.utils.logger import setup_logger, get_logger
from scripts.utils.git_manager import GitManager
from scripts.crawler import WoshipmCrawler
from scripts.summarizer import ArticleSummarizer

class KnowledgeWorkflow:
    """知识库工作流"""

    def __init__(self, config_path: str = "config/config.yaml"):
        """初始化工作流

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

        # 初始化组件
        self.crawler = WoshipmCrawler(config_path)
        self.summarizer = ArticleSummarizer(config_path)

        # Git配置
        git_config = self.config.get('git', {})
        self.git_manager = GitManager(
            repo_path=".",
            remote=git_config.get('remote', 'origin'),
            branch=git_config.get('branch', 'main')
        )
        # 初始化Git仓库
        self.git_manager.init_repo()
        self.auto_push = git_config.get('auto_push', True)
        self.commit_prefix = git_config.get('commit_message_prefix', '[Knowledge DB]')

    def run_crawl(self) -> List[Dict]:
        """执行爬取任务

        Returns:
            爬取的文章列表
        """
        self.logger.info("=" * 50)
        self.logger.info("开始执行爬取任务")
        self.logger.info("=" * 50)

        try:
            articles = self.crawler.crawl_all()
            self.logger.info(f"爬取完成，共 {len(articles)} 篇新文章")
            return articles
        except Exception as e:
            self.logger.error(f"爬取任务失败: {e}")
            return []

    def run_summarize(self) -> int:
        """执行总结任务

        Returns:
            总结的文章数量
        """
        self.logger.info("=" * 50)
        self.logger.info("开始执行总结任务")
        self.logger.info("=" * 50)

        try:
            count = self.summarizer.process_today()
            self.logger.info(f"总结完成，共 {count} 篇文章")
            return count
        except Exception as e:
            self.logger.error(f"总结任务失败: {e}")
            return 0

    def run_git_operations(self, articles_count: int):
        """执行Git操作

        Args:
            articles_count: 文章数量
        """
        self.logger.info("=" * 50)
        self.logger.info("开始执行Git操作")
        self.logger.info("=" * 50)

        try:
            # 初始化Git仓库
            if not self.git_manager.init_repo():
                self.logger.error("Git仓库初始化失败")
                return

            # 检查是否有更改
            status = self.git_manager.get_status()
            if status.get('clean', True):
                self.logger.info("没有更改需要提交")
                return

            # 构建提交信息
            today = datetime.now().strftime("%Y-%m-%d")
            commit_message = f"{self.commit_prefix} 更新知识库 ({today}) - {articles_count}篇新文章"

            # 提交并推送
            if self.auto_push:
                success = self.git_manager.commit_and_push(commit_message)
                if success:
                    self.logger.info("Git操作完成：已提交并推送到远程仓库")
                else:
                    self.logger.error("Git操作失败")
            else:
                success = self.git_manager.commit(commit_message)
                if success:
                    self.logger.info("Git操作完成：已提交（未推送）")
                else:
                    self.logger.error("Git操作失败")

        except Exception as e:
            self.logger.error(f"Git操作失败: {e}")

    def run_full_workflow(self):
        """执行完整工作流"""
        self.logger.info("=" * 60)
        self.logger.info("开始执行完整工作流")
        self.logger.info("=" * 60)

        start_time = datetime.now()

        # 步骤1：爬取
        articles = self.run_crawl()

        # 步骤2：总结
        summarized_count = self.run_summarize()

        # 步骤3：Git操作
        self.run_git_operations(len(articles))

        # 计算耗时
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        self.logger.info("=" * 60)
        self.logger.info("工作流执行完成")
        self.logger.info(f"爬取文章数: {len(articles)}")
        self.logger.info(f"总结文章数: {summarized_count}")
        self.logger.info(f"总耗时: {duration:.2f}秒")
        self.logger.info("=" * 60)

        return {
            'crawled': len(articles),
            'summarized': summarized_count,
            'duration': duration
        }

    def run_crawl_only(self):
        """仅执行爬取"""
        self.logger.info("执行爬取任务")
        articles = self.run_crawl()
        return len(articles)

    def run_summarize_only(self, process_all: bool = False):
        """仅执行总结

        Args:
            process_all: 是否处理所有文章
        """
        self.logger.info("执行总结任务")
        if process_all:
            count = self.summarizer.process_all()
        else:
            count = self.summarizer.process_today()
        return count

    def run_git_only(self):
        """仅执行Git操作"""
        self.logger.info("执行Git操作")
        self.run_git_operations(0)

    def get_status(self) -> Dict:
        """获取系统状态

        Returns:
            状态信息
        """
        # 读取索引
        index_file = Path("data/index.json")
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                index = json.load(f)
        else:
            index = {'articles': {}, 'last_crawl': None}

        # 统计信息
        total_articles = len(index.get('articles', {}))
        summarized_articles = sum(
            1 for a in index.get('articles', {}).values()
            if a.get('summarized', False)
        )

        # Git状态
        git_status = self.git_manager.get_status()

        return {
            'total_articles': total_articles,
            'summarized_articles': summarized_articles,
            'pending_summaries': total_articles - summarized_articles,
            'last_crawl': index.get('last_crawl'),
            'git_status': git_status
        }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='产品经理知识库工作流')
    parser.add_argument('--config', default='config/config.yaml', help='配置文件路径')
    parser.add_argument('--mode', choices=['full', 'crawl', 'summarize', 'git', 'status'],
                       default='full', help='运行模式')
    parser.add_argument('--all', action='store_true', help='处理所有文章（用于summarize模式）')

    args = parser.parse_args()

    # 创建工作流实例
    workflow = KnowledgeWorkflow(args.config)

    # 执行相应模式
    if args.mode == 'full':
        result = workflow.run_full_workflow()
        print(f"\n工作流执行完成:")
        print(f"  爬取文章: {result['crawled']} 篇")
        print(f"  总结文章: {result['summarized']} 篇")
        print(f"  耗时: {result['duration']:.2f} 秒")

    elif args.mode == 'crawl':
        count = workflow.run_crawl_only()
        print(f"\n爬取完成: {count} 篇新文章")

    elif args.mode == 'summarize':
        count = workflow.run_summarize_only(args.all)
        print(f"\n总结完成: {count} 篇文章")

    elif args.mode == 'git':
        workflow.run_git_only()
        print("\nGit操作完成")

    elif args.mode == 'status':
        status = workflow.get_status()
        print("\n系统状态:")
        print(f"  总文章数: {status['total_articles']}")
        print(f"  已总结: {status['summarized_articles']}")
        print(f"  待总结: {status['pending_summaries']}")
        print(f"  最后爬取: {status['last_crawl']}")
        print(f"  Git状态: {'干净' if status['git_status'].get('clean', True) else '有更改'}")


if __name__ == "__main__":
    main()
