"""Git操作管理模块"""

import os
from datetime import datetime
from typing import Optional
import git
from loguru import logger

class GitManager:
    """Git仓库管理器"""

    def __init__(self, repo_path: str = ".", remote: str = "origin", branch: str = "main"):
        """初始化Git管理器

        Args:
            repo_path: 仓库路径
            remote: 远程仓库名称
            branch: 分支名称
        """
        self.repo_path = repo_path
        self.remote = remote
        self.branch = branch
        self.repo = None

    def init_repo(self) -> bool:
        """初始化Git仓库

        Returns:
            是否成功
        """
        try:
            if os.path.exists(os.path.join(self.repo_path, '.git')):
                self.repo = git.Repo(self.repo_path)
                logger.info(f"已连接到现有Git仓库: {self.repo_path}")
            else:
                self.repo = git.Repo.init(self.repo_path)
                logger.info(f"已初始化新的Git仓库: {self.repo_path}")
            return True
        except Exception as e:
            logger.error(f"初始化Git仓库失败: {e}")
            return False

    def add_remote(self, remote_url: str) -> bool:
        """添加远程仓库

        Args:
            remote_url: 远程仓库URL

        Returns:
            是否成功
        """
        try:
            if self.remote in [r.name for r in self.repo.remotes]:
                self.repo.delete_remote(self.remote)
            self.repo.create_remote(self.remote, remote_url)
            logger.info(f"已添加远程仓库: {remote_url}")
            return True
        except Exception as e:
            logger.error(f"添加远程仓库失败: {e}")
            return False

    def pull(self) -> bool:
        """拉取远程更新

        Returns:
            是否成功
        """
        try:
            if self.remote not in [r.name for r in self.repo.remotes]:
                logger.warning(f"远程仓库 {self.remote} 不存在")
                return False

            origin = self.repo.remote(self.remote)
            origin.pull(self.branch)
            logger.info("已拉取远程更新")
            return True
        except Exception as e:
            logger.error(f"拉取更新失败: {e}")
            return False

    def commit(self, message: str, files: list = None) -> bool:
        """提交更改

        Args:
            message: 提交信息
            files: 要提交的文件列表，None表示所有更改

        Returns:
            是否成功
        """
        try:
            if files:
                self.repo.index.add(files)
            else:
                self.repo.git.add(A=True)

            # 检查是否有更改
            if not self.repo.index.diff("HEAD") and not self.repo.untracked_files:
                logger.info("没有更改需要提交")
                return True

            self.repo.index.commit(message)
            logger.info(f"已提交更改: {message}")
            return True
        except Exception as e:
            logger.error(f"提交更改失败: {e}")
            return False

    def push(self) -> bool:
        """推送到远程仓库

        Returns:
            是否成功
        """
        try:
            if self.remote not in [r.name for r in self.repo.remotes]:
                logger.warning(f"远程仓库 {self.remote} 不存在")
                return False

            origin = self.repo.remote(self.remote)
            origin.push(self.branch)
            logger.info("已推送到远程仓库")
            return True
        except Exception as e:
            logger.error(f"推送失败: {e}")
            return False

    def commit_and_push(self, message: str, files: list = None) -> bool:
        """提交并推送

        Args:
            message: 提交信息
            files: 要提交的文件列表

        Returns:
            是否成功
        """
        if self.commit(message, files):
            return self.push()
        return False

    def get_status(self) -> dict:
        """获取仓库状态

        Returns:
            状态信息字典
        """
        try:
            return {
                'branch': self.repo.active_branch.name,
                'modified': [item.a_path for item in self.repo.index.diff(None)],
                'staged': [item.a_path for item in self.repo.index.diff("HEAD")],
                'untracked': self.repo.untracked_files,
                'clean': not self.repo.is_dirty()
            }
        except Exception as e:
            logger.error(f"获取状态失败: {e}")
            return {}

    def create_branch(self, branch_name: str) -> bool:
        """创建新分支

        Args:
            branch_name: 分支名称

        Returns:
            是否成功
        """
        try:
            self.repo.git.checkout('-b', branch_name)
            logger.info(f"已创建新分支: {branch_name}")
            return True
        except Exception as e:
            logger.error(f"创建分支失败: {e}")
            return False

    def switch_branch(self, branch_name: str) -> bool:
        """切换分支

        Args:
            branch_name: 分支名称

        Returns:
            是否成功
        """
        try:
            self.repo.git.checkout(branch_name)
            logger.info(f"已切换到分支: {branch_name}")
            return True
        except Exception as e:
            logger.error(f"切换分支失败: {e}")
            return False
