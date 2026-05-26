"""重命名文章脚本 - 使用有意义的标题"""

import os
import sys
import json
import re
from pathlib import Path

import yaml

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.utils.logger import setup_logger

def extract_title_from_summary(summary_content: str) -> str:
    """从总结内容中提取标题

    Args:
        summary_content: 总结内容

    Returns:
        提取的标题
    """
    # 尝试从总结的第一段提取主题
    lines = summary_content.split('\n')

    for i, line in enumerate(lines):
        line = line.strip()
        # 跳过空行和分隔符
        if not line or line.startswith('---') or line.startswith('==='):
            continue

        # 模式1: "文章的核心观点是：..." 或 "本文的核心观点是..."
        if ('核心观点' in line or '核心思想' in line) and ('是' in line or '为' in line):
            # 提取"是"后面的内容作为主题
            match = re.search(r'(?:核心观点|核心思想)[是为：:\s]+(.+?)(?:[。,.]|$)', line)
            if match:
                title = match.group(1).strip()
                # 清理标题，提取关键短语
                title = re.sub(r'["""'']', '', title)
                title = re.sub(r'[*#]', '', title)
                # 如果太长，截取前50个字符
                if len(title) > 50:
                    # 尝试在逗号或句号处截断
                    for sep in ['，', ',', '。', '；']:
                        pos = title.find(sep)
                        if 10 <= pos <= 50:
                            title = title[:pos]
                            break
                    else:
                        title = title[:50]
                if 10 <= len(title) <= 50:
                    return title

        # 模式2: "文章指出了..." 或 "文章揭示了..."
        if line.startswith('文章') and ('指出' in line or '揭示' in line or '分析' in line or '探讨' in line):
            match = re.search(r'文章[指出揭示分析探讨了]+(.+?)(?:[。,.]|$)', line)
            if match:
                title = match.group(1).strip()
                title = re.sub(r'["""'']', '', title)
                title = re.sub(r'[*#]', '', title)
                if 10 <= len(title) <= 50:
                    return title

        # 模式3: "关于"或"介绍"
        if '关于' in line or '介绍' in line:
            match = re.search(r'(?:关于|介绍)[了]?(.+?)(?:的|，|。|$)', line)
            if match:
                title = match.group(1).strip()
                if 5 <= len(title) <= 30:
                    return title

        # 模式4: 查找"### 标题"格式
        if line.startswith('###') and i < 10:
            title = line.lstrip('#').strip()
            # 移除括号内的字数说明
            title = re.sub(r'[（(]\d+字[）)]', '', title).strip()
            if 3 <= len(title) <= 30:
                return title

    return ""

def extract_title_from_content(content: str) -> str:
    """从原始内容中提取标题

    Args:
        content: 原始内容

    Returns:
        提取的标题
    """
    lines = content.split('\n')

    for line in lines[:50]:  # 只检查前50行
        line = line.strip()

        # 跳过空行
        if not line:
            continue

        # 查找标题格式
        if line.startswith('#'):
            title = line.lstrip('#').strip()
            if 5 <= len(title) <= 80:
                return title

        # 查找可能的标题行（较短且有实际内容）
        if 10 <= len(line) <= 50 and not line.startswith('作者') and not line.startswith('发布'):
            # 检查是否像标题
            if any(keyword in line for keyword in ['如何', '为什么', '是什么', '方法', '技巧', '指南', '实战', '案例']):
                return line

    return ""

def generate_safe_filename(title: str, max_length: int = 50) -> str:
    """生成安全的文件名

    Args:
        title: 原始标题
        max_length: 最大长度

    Returns:
        安全的文件名
    """
    # 移除或替换不安全字符
    safe_title = re.sub(r'[<>:"/\\|?*]', '', title)
    safe_title = re.sub(r'\s+', '_', safe_title)
    safe_title = safe_title.strip('_')

    # 截断到最大长度
    if len(safe_title) > max_length:
        safe_title = safe_title[:max_length]

    # 确保文件名不为空
    if not safe_title:
        safe_title = "未命名文章"

    return safe_title

def rename_articles():
    """重命名文章"""
    # 加载配置
    with open('config/config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # 初始化日志
    logger = setup_logger(
        config.get('logging', {}).get('file', 'logs/crawler.log'),
        config.get('logging', {}).get('level', 'INFO')
    )

    # 目录
    raw_dir = Path("data/raw")
    processed_dir = Path("data/processed")
    kb_dir = Path("knowledge_base")

    # 统计
    total_files = 0
    renamed_files = 0
    errors = []

    logger.info("开始重命名文章...")

    # 遍历所有知识库文件
    for category_dir in kb_dir.iterdir():
        if not category_dir.is_dir() or category_dir.name.startswith('.'):
            continue

        for date_dir in category_dir.iterdir():
            if not date_dir.is_dir():
                continue

            for md_file in date_dir.glob("*.md"):
                total_files += 1

                try:
                    # 读取文件内容
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 提取当前标题
                    current_title = md_file.stem

                    # 如果已经是好的标题，跳过
                    if not current_title.startswith('文章_'):
                        logger.info(f"跳过（已有好标题）: {md_file.name}")
                        continue

                    # 从内容中提取标题
                    title = ""

                    # 方法1: 从文件内容的第一行提取
                    first_line = content.split('\n')[0].strip()
                    if first_line.startswith('#'):
                        title = first_line.lstrip('#').strip()

                    # 方法2: 从原始数据中提取
                    if not title or title.startswith('文章_'):
                        # 提取文章ID
                        article_id = current_title.replace('文章_', '')
                        raw_file = raw_dir / date_dir.name / f"{article_id}.json"

                        if raw_file.exists():
                            with open(raw_file, 'r', encoding='utf-8') as f:
                                raw_data = json.load(f)
                            title = raw_data.get('title', '')

                    # 方法3: 从总结内容中提取
                    if not title or title.startswith('文章_'):
                        title = extract_title_from_summary(content)

                    # 方法4: 从原始内容中提取
                    if not title or title.startswith('文章_'):
                        title = extract_title_from_content(content)

                    # 如果还是没有好标题，使用ID
                    if not title or title.startswith('文章_'):
                        logger.warning(f"无法提取标题: {md_file.name}")
                        continue

                    # 生成新文件名
                    new_filename = generate_safe_filename(title) + '.md'
                    new_path = md_file.parent / new_filename

                    # 检查是否已存在同名文件
                    if new_path.exists() and new_path != md_file:
                        # 添加ID后缀
                        article_id = current_title.replace('文章_', '')
                        new_filename = f"{generate_safe_filename(title)}_{article_id}.md"
                        new_path = md_file.parent / new_filename

                    # 重命名文件
                    if new_path != md_file:
                        md_file.rename(new_path)
                        renamed_files += 1
                        logger.info(f"已重命名: {md_file.name} -> {new_filename}")

                except Exception as e:
                    errors.append(f"{md_file}: {e}")
                    logger.error(f"重命名失败: {md_file} - {e}")

    logger.info(f"重命名完成: {renamed_files}/{total_files} 个文件")

    if errors:
        logger.warning(f"有 {len(errors)} 个错误:")
        for error in errors:
            logger.warning(f"  {error}")

    return renamed_files, total_files, errors

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='重命名文章')
    parser.add_argument('--dry-run', action='store_true', help='仅显示要重命名的文件，不实际修改')

    args = parser.parse_args()

    if args.dry_run:
        print("预览模式：显示要重命名的文件")
        # TODO: 实现预览模式
    else:
        renamed, total, errors = rename_articles()
        print(f"重命名完成: {renamed}/{total} 个文件")
        if errors:
            print(f"有 {len(errors)} 个错误")

if __name__ == "__main__":
    main()
