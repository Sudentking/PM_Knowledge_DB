"""定时运行工作流脚本"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.workflow import KnowledgeWorkflow

def setup_run_logger():
    """设置运行日志"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # 按日期命名日志文件
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"workflow_{today}.log"

    # 配置日志
    logger = logging.getLogger("workflow_runner")
    logger.setLevel(logging.INFO)

    # 文件处理器
    fh = logging.FileHandler(log_file, encoding='utf-8')
    fh.setLevel(logging.INFO)

    # 控制台处理器
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # 格式
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger

def main():
    """主函数"""
    logger = setup_run_logger()

    logger.info("=" * 60)
    logger.info("开始运行知识库工作流")
    logger.info(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    try:
        # 创建工作流实例
        workflow = KnowledgeWorkflow()

        # 运行完整工作流
        result = workflow.run_full_workflow()

        logger.info("-" * 40)
        logger.info("运行结果:")
        logger.info(f"  爬取文章: {result['crawled']} 篇")
        logger.info(f"  总结文章: {result['summarized']} 篇")
        logger.info(f"  重命名文章: {result.get('renamed', 0)} 篇")
        logger.info(f"  运行耗时: {result['duration']:.2f} 秒")
        logger.info("-" * 40)
        logger.info("工作流运行完成")

    except Exception as e:
        logger.error(f"工作流运行失败: {e}")
        logger.exception(e)
        sys.exit(1)

if __name__ == "__main__":
    main()
