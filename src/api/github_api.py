#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GitHub API访问层，负责与GitHub API的交互
"""

from github import Github
import github.Auth


class GitHubAPI:
    """
    GitHub API访问类，提供与GitHub API交互的方法
    """
    
    def __init__(self, access_token):
        """
        初始化GitHubAPI实例
        :param access_token: GitHub个人访问令牌
        """
        self.access_token = access_token
        # 使用新的认证方式
        auth = github.Auth.Token(access_token)
        self.g = Github(auth=auth)
    
    def get_repo(self, repo_owner, repo_name):
        """
        获取指定仓库
        :param repo_owner: 仓库所有者
        :param repo_name: 仓库名称
        :return: 仓库对象
        """
        try:
            repo = self.g.get_repo(f"{repo_owner}/{repo_name}")
            return repo
        except Exception as e:
            print(f"获取仓库失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_issues(self, repo, state="all", labels=None):
        """
        获取仓库的Issues
        :param repo: 仓库对象
        :param state: Issues状态 (open, closed, all)
        :param labels: 标签列表，用于过滤
        :return: Issues迭代器
        """
        try:
            if labels:
                issues = repo.get_issues(state=state, labels=labels)
            else:
                issues = repo.get_issues(state=state)
            return issues
        except Exception as e:
            print(f"获取Issues失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_commits(self, repo, since=None, until=None):
        """
        获取仓库的Commits
        :param repo: 仓库对象
        :param since: 开始日期
        :param until: 结束日期
        :return: Commits迭代器
        """
        try:
            # 根据since和until是否为None，构造不同的调用参数
            if since is not None and until is not None:
                commits = repo.get_commits(since=since, until=until)
            elif since is not None:
                commits = repo.get_commits(since=since)
            elif until is not None:
                commits = repo.get_commits(until=until)
            else:
                # 当since和until都为None时，不传递这些参数
                commits = repo.get_commits()
            print(commits)
            return commits
        except Exception as e:
            print(f"获取Commits失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_pull_requests(self, repo, state="all"):
        """
        获取仓库的Pull Requests
        :param repo: 仓库对象
        :param state: PR状态 (open, closed, all)
        :return: Pull Requests迭代器
        """
        try:
            pulls = repo.get_pulls(state=state)
            return pulls
        except Exception as e:
            print(f"获取Pull Requests失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_contents(self, repo, path="."):
        """
        获取仓库指定路径的内容
        :param repo: 仓库对象
        :param path: 路径
        :return: 内容对象
        """
        try:
            contents = repo.get_contents(path)
            return contents
        except Exception as e:
            print(f"获取内容失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_file_content(self, repo, file_path):
        """
        获取指定文件的内容
        :param repo: 仓库对象
        :param file_path: 文件路径
        :return: 文件内容
        """
        try:
            content = repo.get_contents(file_path)
            if content.encoding == "base64":
                import base64
                return base64.b64decode(content.content).decode('utf-8', errors='replace')
            else:
                return content.content
        except Exception as e:
            print(f"获取文件内容失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
