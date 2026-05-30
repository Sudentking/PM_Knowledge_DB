#!/usr/bin/env python3
"""
手动同步脚本：将 PM_Knowledge_DB 的内容同步到 personal-llm-wiki
用于本地测试或 GitHub Actions 失败时的备用方案
"""

import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

# 配置路径
PM_KB_DIR = Path("D:/code/Knowledge_DB/knowledge_base")
WIKI_RAW_PM_DIR = Path("D:/code/personal-llm-wiki/raw/pm")
WIKI_DIR = Path("D:/code/personal-llm-wiki")

def sync_content():
    """同步内容"""
    print("=" * 50)
    print("开始同步 PM 知识库到 Wiki")
    print("=" * 50)

    # 检查源目录
    if not PM_KB_DIR.exists():
        print(f"错误：源目录不存在：{PM_KB_DIR}")
        return False

    # 创建目标目录
    WIKI_RAW_PM_DIR.mkdir(parents=True, exist_ok=True)

    # 删除旧内容
    print("删除旧内容...")
    for item in WIKI_RAW_PM_DIR.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    # 复制新内容
    print("复制新内容...")
    for item in PM_KB_DIR.iterdir():
        if item.name.startswith('.'):
            continue  # 跳过隐藏文件

        dest = WIKI_RAW_PM_DIR / item.name
        if item.is_dir():
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)

    print(f"同步完成：{PM_KB_DIR} -> {WIKI_RAW_PM_DIR}")
    return True


def git_commit_and_push():
    """Git 提交并推送"""
    print("\n" + "=" * 50)
    print("提交到 Git")
    print("=" * 50)

    os.chdir(WIKI_DIR)

    # 检查是否有变化
    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if not result.stdout.strip():
        print("没有变化需要提交")
        return True

    # 添加文件
    print("添加文件...")
    subprocess.run(["git", "add", "raw/pm/"])

    # 提交
    commit_msg = f"sync: Update PM knowledge from {datetime.now().strftime('%Y-%m-%d')}"
    print(f"提交：{commit_msg}")
    subprocess.run(["git", "commit", "-m", commit_msg])

    # 推送
    print("推送到远程...")
    result = subprocess.run(["git", "push"], capture_output=True, text=True)

    if result.returncode == 0:
        print("推送成功！")
        return True
    else:
        print(f"推送失败：{result.stderr}")
        return False


def main():
    """主函数"""
    # 同步内容
    if not sync_content():
        return

    # Git 提交
    git_commit_and_push()

    print("\n" + "=" * 50)
    print("同步完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()
