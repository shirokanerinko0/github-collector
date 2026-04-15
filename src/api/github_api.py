#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GitHub API访问层，负责与GitHub API的交互
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from github import Github
from src.utils.utils import load_config
import github.Auth
import json
import logging
from datetime import datetime

# 尝试从main.py导入全局配置变量
CONFIG = load_config()

limits = CONFIG["limits"]
# 全局DEBUG变量，用于控制debug模式
DEBUG = True

class GitHubAPI:
    """
    GitHub API访问类，提供与GitHub API交互的方法
    """
    
    def __init__(self, access_token=CONFIG["token"], debug=None, log_dir="logs"):
        """
        初始化GitHubAPI实例
        :param access_token: GitHub个人访问令牌
        :param debug: 是否开启debug模式，输出API调用详情。如果为None，则使用配置文件或全局DEBUG变量
        :param log_dir: 日志文件保存目录
        """
        self.access_token = access_token
        # 优先使用传入的debug参数
        if debug is not None:
            self.debug = debug
        # 其次使用配置文件中的debug值
        elif CONFIG and "debug" in CONFIG:
            self.debug = CONFIG["debug"]
        # 最后使用全局DEBUG变量
        else:
            self.debug = DEBUG
        self.log_dir = log_dir
        
        # 初始化日志
        if self.debug:
            self._init_logger()
        
        # 使用新的认证方式
        auth = github.Auth.Token(access_token)
        self.g = Github(auth=auth)
    
    def _init_logger(self):
        """
        初始化日志记录器
        """
        # 确保日志目录存在
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 创建日志文件路径
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(self.log_dir, f"github_api_debug_{timestamp}.log")
        
        # 配置日志
        logging.basicConfig(
            filename=log_file,
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            encoding='utf-8'
        )
        
        self.logger = logging.getLogger(__name__)
        print(f"Debug模式已开启，日志将保存到: {log_file}")
    
    def _log_api_response(self, api_url, response_data):
        """
        记录API响应到日志
        :param api_url: API请求URL
        :param response_data: API响应数据
        """
        if self.debug and hasattr(self, 'logger'):
            try:
                # 确保数据可序列化
                if isinstance(response_data, (list, dict)):
                    serialized_data = json.dumps(response_data, ensure_ascii=False, indent=2)
                else:
                    serialized_data = str(response_data)
                
                log_message = f"API URL: {api_url}\nResponse: {serialized_data}"
                self.logger.debug(log_message)
            except Exception as e:
                self.logger.error(f"记录API响应失败: {str(e)}")
    
    def get_repo(self, repo_owner, repo_name):
        """
        获取指定仓库
        :param repo_owner: 仓库所有者
        :param repo_name: 仓库名称
        :return: 仓库对象
        """
        api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        
        try:
            repo = self.g.get_repo(f"{repo_owner}/{repo_name}")
            
            # 记录API响应
            if self.debug:
                repo_data = {
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "description": repo.description,
                    "html_url": repo.html_url,
                    "stargazers_count": repo.stargazers_count,
                    "forks_count": repo.forks_count,
                    "open_issues_count": repo.open_issues_count
                }
                self._log_api_response(api_url, repo_data)
            
            return repo
        except Exception as e:
            print(f"获取仓库失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_issues(self, repo, state="all", labels=[]):
        """
        获取仓库的Issues
        :param repo: 仓库对象
        :param state: Issues状态 (open, closed, all)
        :param labels: 标签列表，用于过滤
        :return: Issues列表
        """
        api_url = f"https://api.github.com/repos/{repo.owner.login}/{repo.name}/issues"
        params = f"?state={state}"
        if labels:
            params += f"&labels={','.join(labels)}"
        api_url += params
        
        try:
            ## 返回issues迭代器
            issues = repo.get_issues(state=state, labels=labels)
            issue_list = []
            count = 0
            for issue in issues:
                if count >= limits["max_issues"]:
                    break
                if "pull_request" in issue.raw_data:
                    continue
                issue_list.append(issue)
                print(f"当前获取到第 {count+1} 个Issue: {issue.title}")
                count += 1
            # 记录API响应
            if self.debug:
                issues_data = []
                for issue in issue_list:  
                    issues_data.append({
                        "number": issue.number,
                        "title": issue.title,
                        "state": issue.state,
                        "events_url": issue.events_url,
                        "created_at": issue.created_at.isoformat() if issue.created_at else None,
                        "user": issue.user.login if issue.user else None,
                        "labels": [label.name for label in issue.labels]
                    })
                self._log_api_response(api_url, issues_data)
            
            return issue_list
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
        api_url = f"https://api.github.com/repos/{repo.owner.login}/{repo.name}/commits"
        params = []
        if since:
            params.append(f"since={since.isoformat()}")
        if until:
            params.append(f"until={until.isoformat()}")
        if params:
            api_url += "?" + "&".join(params)
        
        try:
            kwargs = {}
            if since is not None:
                kwargs["since"] = since
            if until is not None:
                kwargs["until"] = until

            commits = repo.get_commits(**kwargs)
            commits_list = []
            count = 0
            for commit in commits:
                if count >= limits["max_commits"]:
                    break
                commits_list.append(commit)
                count += 1
            
            # 记录API响应
            if self.debug:
                commits_data = []
                for commit in commits_list:  # 只记录前10个，避免日志过大
                    commits_data.append({
                        "sha": commit.sha,
                        "message": commit.commit.message,
                        "author": commit.commit.author.name if commit.commit.author else None,
                        "date": commit.commit.author.date.isoformat() if commit.commit.author and commit.commit.author.date else None
                    })
                self._log_api_response(api_url, commits_data)
            
            return commits_list
        except Exception as e:
            print(f"获取Commits失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_pull_requests(self, repo, state="closed"):
        """
        获取仓库的Pull Requests，包含关联的commit列表
        :param repo: 仓库对象
        :param state: PR状态 (open, closed, all)
        :return: Pull Requests列表
        """
        api_url = f"https://api.github.com/repos/{repo.owner.login}/{repo.name}/pulls?state={state}"
        
        try:
            pulls = repo.get_pulls(state=state)
            pulls_list = []
            count = 0
            for pr in pulls:
                if count >= limits["max_pull_requests"]:
                    break
                if CONFIG["pr_filter_labels"]: 
                    labels = [label.name for label in pr.labels]
                    if not any(label in CONFIG["pr_filter_labels"] for label in labels):
                        continue
                if not pr.merged and CONFIG.get("filter_unmerged_pr", True):
                    continue
                pulls_list.append(pr)
                print(f"当前获取到第 {count+1} 个PR: {pr.title}")
                count += 1
            
            # # 记录API响应
            # if self.debug:
            #     pulls_data = []
            #     for pr in pulls_list:
            #         # 获取PR关联的commits
            #         pr_commits = []
            #         try:
            #             commits = pr.get_commits()
            #             for commit in commits:
            #                 commit_info = {
            #                     "sha": commit.sha,
            #                     "message": commit.commit.message,
            #                     "author": {
            #                         "name": commit.commit.author.name if commit.commit.author else None,
            #                         "date": commit.commit.author.date.isoformat() if commit.commit.author and commit.commit.author.date else None
            #                     },
            #                     "url": commit.html_url
            #                 }
            #                 pr_commits.append(commit_info)
            #         except Exception as e:
            #             print(f"获取PR {pr.number} 的commits失败: {str(e)}")
                    
            #         pulls_data.append({
            #             "number": pr.number,
            #             "title": pr.title,
            #             "state": pr.state,
            #             "created_at": pr.created_at.isoformat() if pr.created_at else None,
            #             "merged": pr.merged,
            #             "merged_at": pr.merged_at.isoformat() if pr.merged_at else None,
            #             "user": pr.user.login if pr.user else None,
            #             "head": pr.head.ref,
            #             "base": pr.base.ref,
            #             "commits": pr_commits
            #         })
            #     self._log_api_response(api_url, pulls_data)
            #     # 重新获取pulls迭代器，因为之前的已经被消费
            return pulls_list
        except Exception as e:
            print(f"获取Pull Requests失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_commit_detail(self, repo, commit_hash):
        """
        获取commit的详细信息，包括文件具体变动
        :param repo: 仓库对象
        :param commit_hash: commit的SHA哈希值
        :return: 包含commit详细信息的字典
        """
        api_url = f"https://api.github.com/repos/{repo.owner.login}/{repo.name}/commits/{commit_hash}"
        
        try:
            commit = repo.get_commit(commit_hash)
            
            # 提取commit基本信息
            commit_detail = {
                "sha": commit.sha,
                "message": commit.commit.message,
                "url": commit.html_url,
                "stats": {
                    "additions": commit.stats.additions,
                    "deletions": commit.stats.deletions,
                    "total": commit.stats.total
                },
                "files": []
            }
            
            # 提取文件变动信息
            for file in commit.files:
                file_change = {
                    "filename": file.filename,
                    "changes": file.changes,
                    "additions": file.additions,
                    "deletions": file.deletions,
                    "status": file.status,
                    "patch": file.patch,
                    "blob_url": file.blob_url,
                    "raw_url": file.raw_url,
                    "contents_url": file.contents_url
                }
                commit_detail["files"].append(file_change)
            
            # 记录API响应
            if self.debug:
                # 只记录文件信息摘要，不记录完整的patch，避免日志过大
                commit_data = commit_detail.copy()
                commit_data["files"] = [
                    {
                        "filename": f["filename"],
                        "changes": f["changes"],
                        "additions": f["additions"],
                        "deletions": f["deletions"],
                        "status": f["status"],
                        "patch": f["patch"]
                    }
                    for f in commit_data["files"]
                ]
                self._log_api_response(api_url, commit_data)
            
            return commit_detail
        except Exception as e:
            print(f"获取commit详细信息失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_contents(self, repo, path="."):
        """
        获取仓库指定路径的内容
        :param repo: 仓库对象
        :param path: 路径
        :return: 内容对象
        """
        api_url = f"https://api.github.com/repos/{repo.owner.login}/{repo.name}/contents/{path}"
        
        try:
            contents = repo.get_contents(path)
            
            # 记录API响应
            if self.debug:
                contents_data = []
                for content in contents:
                    content_info = {
                        "name": content.name,
                        "path": content.path,
                        "type": content.type,
                        "size": content.size,
                        "download_url": content.download_url
                    }
                    contents_data.append(content_info)
                self._log_api_response(api_url, contents_data)
            
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
        api_url = f"https://api.github.com/repos/{repo.owner.login}/{repo.name}/contents/{file_path}"
        
        try:
            content = repo.get_contents(file_path)
            
            # 获取文件内容
            if content.encoding == "base64":
                import base64
                file_content = base64.b64decode(content.content).decode('utf-8', errors='replace')
            else:
                file_content = content.content
            
            # 记录API响应（只记录文件信息，不记录文件内容，避免日志过大）
            if self.debug:
                file_info = {
                    "name": content.name,
                    "path": content.path,
                    "size": content.size,
                    "encoding": content.encoding,
                    "content_length": len(file_content) if file_content else 0
                }
                self._log_api_response(api_url, file_info)
            
            return file_content
        except Exception as e:
            print(f"获取文件内容失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_issue_commit_refs(self, repo, issue):
        """
        获取Issue关联的commit引用
        :param repo: 仓库对象
        :param issue: Issue对象
        :return: commit引用列表
        """
        try:
            # 获取issue事件
            events = issue.get_events()
            commit_refs = []
            
            for event in events:
                # 只处理引用了commit的事件
                if event.commit_id is not None and self.is_commit_in_repo(repo, event.commit_id):
                    try:
                        # 直接从事件中构建commit信息
                        commit_refs.append({
                            "event_id": event.id,
                            "event_type": event.event,
                            "commit_sha": event.commit_id,
                            "message": f"Commit referenced in issue: {issue.title}",
                            "commit_url": event.commit_url,
                            "created_at": event.created_at.isoformat() if event.created_at else None
                        })
                    except Exception as e:
                        print(f"处理commit {event.commit_id} 失败: {str(e)}")
                        continue
            
            return commit_refs
        except Exception as e:
            print(f"获取Issue commit引用失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

    def is_commit_in_repo(self, repo, commit_hash):
        """
        判断给定的commit_hash是否属于指定的仓库
        :param repo: 仓库对象
        :param commit_hash: commit的SHA哈希值
        :return: 如果commit属于该仓库返回True，否则返回False
        """
        api_url = f"https://api.github.com/repos/{repo.owner.login}/{repo.name}/commits/{commit_hash}"
        
        try:
            # 尝试获取commit信息
            repo.get_commit(commit_hash)
            # 如果成功获取commit，说明commit属于该仓库
            return True
        except Exception as e:
            # 如果获取失败，说明commit不属于该仓库
            if self.debug:
                error_data = {
                    "error": str(e),
                    "commit_hash": commit_hash,
                    "repo": f"{repo.owner.login}/{repo.name}"
                }
                self._log_api_response(api_url, error_data)
            return False

    def get_issue_change_files (self, repo, issue):
        """
        获取Issue关联的提交中修改的文件
        :param repo: 仓库对象
        :param issue: Issue对象
        :return: 修改文件列表
        """
        # 获取issue关联的commit引用
        commit_refs = self.get_issue_commit_refs(repo, issue)
        
        modify_files = []
        for ref in commit_refs:
            commit_sha = ref['commit_sha']
            try:
                # 获取commit的修改文件
                commit = repo.get_commit(commit_sha)
                files = commit.files
                for file in files:
                    ## 只记录代码文件
                    if file.filename.endswith(tuple(CONFIG["source_code_extensions"])):
                        modify_files.append({
                            "commit_sha": commit_sha,
                            "file_path": file.filename,
                            "status": file.status,
                            "additions": file.additions,
                            "deletions": file.deletions,
                            "changes": file.changes,
                            "patch": file.patch
                        })
            except Exception as e:
                print(f"获取commit {commit_sha} 的修改文件失败: {str(e)}")
                continue
        
        return modify_files

    def get_pr_change_files(self, repo, pr):
        """
        获取Pull Request关联的提交中修改的文件
        :param repo: 仓库对象
        :param pr: Pull Request对象
        :return: 修改文件列表
        """
        # 获取pr关联的commit引用
        files = repo.get_pull(pr.number).get_files()
        modify_files = []
        for file in files:
            ## 只记录代码文件
            if file.filename.endswith(tuple(CONFIG["source_code_extensions"])):
                modify_files.append({
                    "file_path": file.filename,
                    "status": file.status,
                    "additions": file.additions,
                    "deletions": file.deletions,
                    "changes": file.changes,
                    "patch": file.patch
            })
        
        return modify_files


if __name__ == "__main__":
    github_api = GitHubAPI(debug=True)
    
    # 测试获取Issue关联的提交中修改的文件
    repo = github_api.get_repo(CONFIG["owner"], CONFIG["repo"])
    issue = repo.get_issue(1)
    modify_files = github_api.get_issue_change_files(repo, issue)
    print(modify_files)
    
    # 测试获取Pull Request关联的提交中修改的文件
    pr = repo.get_pull(5)
    modify_files = github_api.get_pr_change_files(repo, pr)
    print(modify_files)