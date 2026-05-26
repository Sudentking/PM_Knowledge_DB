"""系统测试脚本"""

import os
import sys
import json
from pathlib import Path

# 设置标准输出编码为UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """测试模块导入"""
    print("测试模块导入...")
    try:
        from scripts.utils.logger import setup_logger, get_logger
        print("  ✓ 日志模块导入成功")
    except Exception as e:
        print(f"  ✗ 日志模块导入失败: {e}")
        return False

    try:
        from scripts.utils.html_parser import ArticleParser, ContentCleaner
        print("  ✓ HTML解析模块导入成功")
    except Exception as e:
        print(f"  ✗ HTML解析模块导入失败: {e}")
        return False

    try:
        from scripts.utils.git_manager import GitManager
        print("  ✓ Git管理模块导入成功")
    except Exception as e:
        print(f"  ✗ Git管理模块导入失败: {e}")
        return False

    try:
        from scripts.crawler import WoshipmCrawler
        print("  ✓ 爬虫模块导入成功")
    except Exception as e:
        print(f"  ✗ 爬虫模块导入失败: {e}")
        return False

    try:
        from scripts.summarizer import ArticleSummarizer
        print("  ✓ 总结模块导入成功")
    except Exception as e:
        print(f"  ✗ 总结模块导入失败: {e}")
        return False

    try:
        from scripts.workflow import KnowledgeWorkflow
        print("  ✓ 工作流模块导入成功")
    except Exception as e:
        print(f"  ✗ 工作流模块导入失败: {e}")
        return False

    return True

def test_config():
    """测试配置文件"""
    print("\n测试配置文件...")
    try:
        import yaml

        config_path = Path("config/config.yaml")
        if not config_path.exists():
            print(f"  ✗ 配置文件不存在: {config_path}")
            return False

        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # 检查必要的配置项
        required_keys = ['crawler', 'summarizer', 'git', 'schedule']
        for key in required_keys:
            if key in config:
                print(f"  ✓ 配置项 {key} 存在")
            else:
                print(f"  ✗ 配置项 {key} 缺失")
                return False

        print("  ✓ 配置文件格式正确")
        return True
    except Exception as e:
        print(f"  ✗ 配置文件测试失败: {e}")
        return False

def test_directory_structure():
    """测试目录结构"""
    print("\n测试目录结构...")

    required_dirs = [
        "config",
        "scripts",
        "scripts/utils",
        "data",
        "data/raw",
        "data/processed",
        "knowledge_base",
        "knowledge_base/product-design",
        "knowledge_base/user-research",
        "knowledge_base/data-analysis",
        "knowledge_base/project-management",
        "knowledge_base/strategy",
        "knowledge_base/industry-insights",
        "logs"
    ]

    all_exist = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"  ✓ 目录存在: {dir_path}")
        else:
            print(f"  ✗ 目录缺失: {dir_path}")
            all_exist = False

    return all_exist

def test_git_repo():
    """测试Git仓库"""
    print("\n测试Git仓库...")
    try:
        import git

        repo_path = Path(".")
        if not (repo_path / ".git").exists():
            print("  ✗ Git仓库未初始化")
            return False

        repo = git.Repo(repo_path)
        print(f"  ✓ Git仓库已初始化")
        print(f"  ✓ 当前分支: {repo.active_branch.name}")

        # 检查是否有远程仓库
        if repo.remotes:
            print(f"  ✓ 远程仓库: {[r.name for r in repo.remotes]}")
        else:
            print("  ⚠ 没有配置远程仓库")

        return True
    except Exception as e:
        print(f"  ✗ Git仓库测试失败: {e}")
        return False

def test_data_index():
    """测试数据索引"""
    print("\n测试数据索引...")
    try:
        index_path = Path("data/index.json")
        if not index_path.exists():
            print("  ✗ 索引文件不存在")
            return False

        with open(index_path, 'r', encoding='utf-8') as f:
            index = json.load(f)

        print(f"  ✓ 索引文件存在")
        print(f"  ✓ 文章数量: {len(index.get('articles', {}))}")
        print(f"  ✓ 最后爬取: {index.get('last_crawl', '无')}")

        return True
    except Exception as e:
        print(f"  ✗ 数据索引测试失败: {e}")
        return False

def test_api_key():
    """测试API Key配置"""
    print("\n测试API Key配置...")

    api_key = os.environ.get('OPENAI_API_KEY')
    if api_key:
        print(f"  ✓ OPENAI_API_KEY 已设置")
        print(f"  ✓ API Key 长度: {len(api_key)} 字符")
        return True
    else:
        print("  ⚠ OPENAI_API_KEY 未设置")
        print("  请设置环境变量: set OPENAI_API_KEY=your_api_key")
        return False

def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("产品经理知识库系统测试")
    print("=" * 60)

    tests = [
        ("模块导入", test_imports),
        ("配置文件", test_config),
        ("目录结构", test_directory_structure),
        ("Git仓库", test_git_repo),
        ("数据索引", test_data_index),
        ("API Key", test_api_key),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n测试 {test_name} 发生异常: {e}")
            results.append((test_name, False))

    # 打印测试结果汇总
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {test_name}: {status}")

    print(f"\n通过率: {passed}/{total} ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n✓ 所有测试通过！系统准备就绪。")
        return True
    else:
        print("\n⚠ 部分测试失败，请检查并修复问题。")
        return False

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='系统测试')
    parser.add_argument('--test', choices=['all', 'imports', 'config', 'dirs', 'git', 'index', 'api'],
                       default='all', help='运行指定测试')

    args = parser.parse_args()

    if args.test == 'all':
        success = run_all_tests()
        sys.exit(0 if success else 1)
    elif args.test == 'imports':
        success = test_imports()
    elif args.test == 'config':
        success = test_config()
    elif args.test == 'dirs':
        success = test_directory_structure()
    elif args.test == 'git':
        success = test_git_repo()
    elif args.test == 'index':
        success = test_data_index()
    elif args.test == 'api':
        success = test_api_key()

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
