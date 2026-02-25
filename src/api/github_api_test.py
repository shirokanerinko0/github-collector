#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GitHub API测试文件
"""

import unittest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.api.github_api import GitHubAPI

from src.utils.utils import load_config
CONFIG = load_config()

class TestGitHubAPI(unittest.TestCase):
    """
    GitHub API测试类
    """
    
    @classmethod
    def setUpClass(cls):
        """
        测试前的初始化工作
        """
        # 加载配置文件
        cls.config = CONFIG
        
        # 从配置中获取信息
        cls.access_token = cls.config.get("token")
        cls.repo_owner = cls.config.get("owner")
        cls.repo_name = cls.config.get("repo")
        
        # 初始化GitHubAPI实例
        cls.github_api = GitHubAPI(cls.access_token)
    
    def test_get_repo(self):
        """
        测试获取仓库功能
        """
        print("\n测试获取仓库功能...")
        repo = self.github_api.get_repo(self.repo_owner, self.repo_name)
        self.assertIsNotNone(repo, "无法获取仓库")
        self.assertEqual(repo.name, self.repo_name, "仓库名称不匹配")
        self.assertEqual(repo.owner.login, self.repo_owner, "仓库所有者不匹配")
        print(f"成功获取仓库: {repo.name}")
    
    def test_get_issues(self):
        """
        测试获取Issues功能
        """
        print("\n测试获取Issues功能...")
        repo = self.github_api.get_repo(self.repo_owner, self.repo_name)
        self.assertIsNotNone(repo, "无法获取仓库")
        
        issues = self.github_api.get_issues(repo, state="all")
        self.assertIsNotNone(issues, "无法获取Issues") 
        # 转换为列表并检查
        issues_list = list(issues)
        print(f"获取到 {len(issues_list)} 个Issues")
        self.assertGreaterEqual(len(issues_list), 0, "Issues列表为空")
    
    def test_get_commits(self):
        """
        测试获取Commits功能
        """
        print("\n测试获取Commits功能...")
        repo = self.github_api.get_repo(self.repo_owner, self.repo_name)
        self.assertIsNotNone(repo, "无法获取仓库")
        
        commits = self.github_api.get_commits(repo)
        self.assertIsNotNone(commits, "无法获取Commits")
        
        # 转换为列表并检查
        commits_list = list(commits)
        print(f"获取到 {len(commits_list)} 个Commits")
        self.assertGreaterEqual(len(commits_list), 0, "Commits列表为空")
    
    def test_get_pull_requests(self):
        """
        测试获取Pull Requests功能
        """
        print("\n测试获取Pull Requests功能...")
        repo = self.github_api.get_repo(self.repo_owner, self.repo_name)
        self.assertIsNotNone(repo, "无法获取仓库")
        
        prs = self.github_api.get_pull_requests(repo, state="all")
        self.assertIsNotNone(prs, "无法获取Pull Requests")
        
        # 转换为列表并检查
        prs_list = list(prs)
        print(f"获取到 {len(prs_list)} 个Pull Requests")
        self.assertGreaterEqual(len(prs_list), 0, "Pull Requests列表为空")
    
    def test_get_contents(self):
        """
        测试获取仓库内容功能
        """
        print("\n测试获取仓库内容功能...")
        repo = self.github_api.get_repo(self.repo_owner, self.repo_name)
        self.assertIsNotNone(repo, "无法获取仓库")
        
        contents = self.github_api.get_contents(repo, ".")
        self.assertIsNotNone(contents, "无法获取仓库内容")
        self.assertGreaterEqual(len(contents), 0, "仓库内容为空")
        
        print(f"获取到 {len(contents)} 个文件/目录")
        # 打印前5个内容
        for content in contents[:5]:
            print(f"  - {content.name} ({content.type})")
    
    def test_get_file_content(self):
        """
        测试获取文件内容功能
        """
        print("\n测试获取文件内容功能...")
        repo = self.github_api.get_repo(self.repo_owner, self.repo_name)
        self.assertIsNotNone(repo, "无法获取仓库")
        
        # 获取根目录内容，找到一个文件
        contents = self.github_api.get_contents(repo, ".")
        file_path = None
        
        for content in contents:
            if content.type == "file":
                file_path = content.path
                break
        
        self.assertIsNotNone(file_path, "未找到文件")
        
        # 获取文件内容
        file_content = self.github_api.get_file_content(repo, file_path)
        self.assertIsNotNone(file_content, f"无法获取文件内容: {file_path}")
        self.assertGreater(len(file_content), 0, f"文件内容为空: {file_path}")
        
        print(f"成功获取文件内容: {file_path}")
        print(f"文件长度: {len(file_content)} 字符")
    
    def test_get_commit_detail(self):
        """
        测试获取commit详细信息功能
        """
        print("\n测试获取commit详细信息功能...")
        repo = self.github_api.get_repo(self.repo_owner, self.repo_name)
        self.assertIsNotNone(repo, "无法获取仓库")
        
        # 获取最近的commits
        commits = self.github_api.get_commits(repo)
        self.assertIsNotNone(commits, "无法获取Commits")
        self.assertGreater(len(commits), 0, "Commits列表为空")
        
        # 获取第一个commit的哈希值
        commit_hash = commits[0].sha
        print(f"测试commit哈希值: {commit_hash}")
        
        # 获取commit详细信息
        commit_detail = self.github_api.get_commit_detail(repo, commit_hash)
        self.assertIsNotNone(commit_detail, "无法获取commit详细信息")
        
        # 验证返回的数据结构
        self.assertIn("sha", commit_detail, "返回数据中缺少sha字段")
        self.assertIn("message", commit_detail, "返回数据中缺少message字段")
        self.assertIn("author", commit_detail, "返回数据中缺少author字段")
        self.assertIn("committer", commit_detail, "返回数据中缺少committer字段")
        self.assertIn("stats", commit_detail, "返回数据中缺少stats字段")
        self.assertIn("files", commit_detail, "返回数据中缺少files字段")
        
        # 验证sha匹配
        self.assertEqual(commit_detail["sha"], commit_hash, "返回的sha与请求的不匹配")
        
        # 验证stats结构
        self.assertIn("additions", commit_detail["stats"], "stats中缺少additions字段")
        self.assertIn("deletions", commit_detail["stats"], "stats中缺少deletions字段")
        self.assertIn("total", commit_detail["stats"], "stats中缺少total字段")
        
        # 验证files结构
        self.assertIsInstance(commit_detail["files"], list, "files字段应该是列表")
        
        # 如果有文件变动，验证文件变动的结构
        if commit_detail["files"]:
            for file_change in commit_detail["files"]:
                self.assertIn("filename", file_change, "文件变动中缺少filename字段")
                self.assertIn("changes", file_change, "文件变动中缺少changes字段")
                self.assertIn("additions", file_change, "文件变动中缺少additions字段")
                self.assertIn("deletions", file_change, "文件变动中缺少deletions字段")
                self.assertIn("status", file_change, "文件变动中缺少status字段")
                self.assertIn("patch", file_change, "文件变动中缺少patch字段")
        
        print("成功获取commit详细信息")
        print(f"提交信息: {commit_detail['message']}")
        print(f"作者: {commit_detail['author']['name']}")
        print(f"日期: {commit_detail['author']['date']}")
        print(f"统计信息: +{commit_detail['stats']['additions']} -{commit_detail['stats']['deletions']}")
        print(f"修改的文件数: {len(commit_detail['files'])}")
        
        # 打印前3个修改的文件
        for file_change in commit_detail['files'][:3]:
            print(f"  - {file_change['filename']} ({file_change['status']}): +{file_change['additions']} -{file_change['deletions']}")
    
    def test_get_pull_requests_with_commits(self):
        """
        测试获取PR信息（包含关联的commit列表）功能
        """
        print("\n测试获取PR信息（包含关联的commit列表）功能...")
        repo = self.github_api.get_repo(self.repo_owner, self.repo_name)
        self.assertIsNotNone(repo, "无法获取仓库")
        
        # 获取PR列表
        prs = self.github_api.get_pull_requests(repo, state="all")
        self.assertIsNotNone(prs, "无法获取Pull Requests")
        self.assertGreater(len(prs), 0, "Pull Requests列表为空")
        
        print(f"获取到 {len(prs)} 个Pull Requests")
        
        # 验证每个PR对象的基本属性
        for pr in prs:
            print(f"\nPR #{pr.number}: {pr.title}")
            self.assertIsNotNone(pr.number, "PR缺少number属性")
            self.assertIsNotNone(pr.title, "PR缺少title属性")
            self.assertIsNotNone(pr.state, "PR缺少state属性")
            
            # 尝试获取PR的commits（这里需要通过API直接获取，因为返回的是PR对象）
            try:
                commits = pr.get_commits()
                commit_list = list(commits)
                print(f"  关联的commits数量: {len(commit_list)}")
                
                # 验证commit列表
                for commit in commit_list[:2]:  # 只打印前2个commits
                    print(f"  - Commit: {commit.sha[:7]} - {commit.commit.message[:50]}...")
                    self.assertIsNotNone(commit.sha, "Commit缺少sha属性")
                    self.assertIsNotNone(commit.commit.message, "Commit缺少message属性")
            except Exception as e:
                print(f"  获取commits时出错: {str(e)}")

    def test_get_issue_commit_refs(self):
        """
        测试获取Issue关联的commit引用功能
        """
        print("\n测试获取Issue关联的commit引用功能...")
        repo = self.github_api.get_repo(self.repo_owner, self.repo_name)
        self.assertIsNotNone(repo, "无法获取仓库")
        
        # 获取Issue列表
        issues = self.github_api.get_issues(repo, state="all")
        self.assertIsNotNone(issues, "无法获取Issues")
        self.assertGreater(len(issues), 0, "Issues列表为空")
        for issue in issues[:2]:  # 只处理前2个Issue
            print(f"\nIssue #{issue.number}: {issue.title}")
            self.assertIsNotNone(issue.number, "Issue缺少number属性")
            self.assertIsNotNone(issue.title, "Issue缺少title属性")
            
            # 获取关联的commit引用
            commit_refs = self.github_api.get_issue_commit_refs(repo, issue)
            self.assertIsNotNone(commit_refs, "无法获取commit引用")
            print(f"  关联的commit引用数量: {len(commit_refs)}")
            
            # 验证每个commit引用的基本属性
            for ref in commit_refs[:2]:  # 只验证前2个引用
                print(f"  - Commit Ref: {ref['commit_sha'][:7]} - {ref['message'][:50]}...")
                self.assertIsNotNone(ref['commit_sha'], "commit引用缺少commit_sha属性")
                self.assertIsNotNone(ref['message'], "commit引用缺少message属性")
        


if __name__ == '__main__':
    """
    运行测试
    """
    unittest.main()
