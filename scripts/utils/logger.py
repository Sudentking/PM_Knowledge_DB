"""日志工具模块"""

import os
import sys
from datetime import datetime
from loguru import logger

def setup_logger(log_file: str = "logs/crawler.log", level: str = "INFO"):
    """配置日志系统

    Args:
        log_file: 日志文件路径
        level: 日志级别
    """
    # 确保日志目录存在
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # 移除默认处理器
    logger.remove()

    # 添加控制台输出
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=level
    )

    # 添加文件输出
    logger.add(
        log_file,
        rotation="10 MB",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=level,
        encoding="utf-8"
    )

    return logger

def get_logger(name: str = None):
    """获取日志器

    Args:
        name: 日志器名称

    Returns:
        日志器实例
    """
    if name:
        return logger.bind(name=name)
    return logger
