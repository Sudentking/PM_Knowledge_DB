"""修复知识库脚本 - 重新生成知识库文件"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

import yaml
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.utils.logger import setup_logger

def fix_knowledge_base():
    """修复知识库"""
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

    # 分类映射
    category_mapping = {
        'pd': 'product-design',
        'it': 'it',
        'ai': 'ai',
        'share': 'share',
        'class': 'class',
        'operate': 'operate',
        'ued': 'ued',
        'dajiang': 'dajiang',
        'weidian': 'weidian',
        'pmdis': 'pmdis'
    }

    # 统计
    total_files = 0
    fixed_files = 0
    errors = []

    logger.info("开始修复知识库...")

    # 遍历所有总结文件
    for date_dir in processed_dir.iterdir():
        if not date_dir.is_dir():
            continue

        for summary_file in date_dir.glob("*_summary.json"):
            total_files += 1

            try:
                # 读取总结文件
                with open(summary_file, 'r', encoding='utf-8') as f:
                    summary_data = json.load(f)

                article_id = summary_data.get('id', '')
                title = summary_data.get('title', '')
                author = summary_data.get('author', '')
                url = summary_data.get('url', '')
                category = summary_data.get('category', '')
                summary = summary_data.get('summary', '')

                # 如果标题为空，尝试从原始文件获取
                if not title:
                    raw_file = raw_dir / date_dir.name / f"{article_id}.json"
                    if raw_file.exists():
                        with open(raw_file, 'r', encoding='utf-8') as f:
                            raw_data = json.load(f)
                        title = raw_data.get('title', '')
                        author = raw_data.get('author', '')

                # 如果还是没有标题，使用ID
                if not title:
                    title = f"文章_{article_id}"

                # 确定分类目录
                kb_category = category_mapping.get(category, 'uncategorized')

                # 创建目录
                target_dir = kb_dir / kb_category / date_dir.name
                target_dir.mkdir(parents=True, exist_ok=True)

                # 生成安全的文件名
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
                if not safe_title:
                    safe_title = f"article_{article_id}"

                # 生成Markdown内容
                markdown = f"""# {title}

**作者**: {author}
**发布时间**: {date_dir.name}
**原文链接**: [{url}]({url})
**分类**: {category}

---

{summary}

---

*本文由AI自动总结生成，仅供参考。*
"""

                # 保存文件
                file_path = target_dir / f"{safe_title}.md"
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(markdown)

                fixed_files += 1
                logger.info(f"已修复: {file_path}")

            except Exception as e:
                errors.append(f"{summary_file}: {e}")
                logger.error(f"修复失败: {summary_file} - {e}")

    # 删除旧的uncategorized目录
    uncategorized_dir = kb_dir / "uncategorized"
    if uncategorized_dir.exists():
        import shutil
        shutil.rmtree(uncategorized_dir)
        logger.info("已删除旧的uncategorized目录")

    # 删除空的.md文件
    for md_file in kb_dir.rglob("*.md"):
        if md_file.name == ".md":
            md_file.unlink()
            logger.info(f"已删除空文件: {md_file}")

    logger.info(f"修复完成: {fixed_files}/{total_files} 个文件")

    if errors:
        logger.warning(f"有 {len(errors)} 个错误:")
        for error in errors:
            logger.warning(f"  {error}")

    return fixed_files, total_files, errors

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='修复知识库')
    parser.add_argument('--dry-run', action='store_true', help='仅显示要修复的文件，不实际修改')

    args = parser.parse_args()

    if args.dry_run:
        print("预览模式：显示要修复的文件")
        # TODO: 实现预览模式
    else:
        fixed, total, errors = fix_knowledge_base()
        print(f"修复完成: {fixed}/{total} 个文件")
        if errors:
            print(f"有 {len(errors)} 个错误")

if __name__ == "__main__":
    main()
