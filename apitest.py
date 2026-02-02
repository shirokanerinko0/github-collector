from src.utils.utils import load_config, save_data
from github import Github
import github.Auth
import json
from datetime import datetime
CONFIG = load_config()


access_token = CONFIG.get("token")
repo_owner = CONFIG.get("owner")
repo_name = CONFIG.get("repo")
filter_labels = CONFIG.get("filter_labels")
max_issues = CONFIG.get("limits").get("max_issues")
auth = github.Auth.Token(access_token)
g = Github(auth=auth)

repo = g.get_repo(f"{repo_owner}/{repo_name}")
print(repo)
save_data(repo.raw_data, "repo_test.json")

def get_issues(repo, state="all", labels=[]):
    """
    获取仓库的Issues
    :param repo: 仓库对象
    :param state: Issues状态 (open, closed, all)
    :param labels: 标签列表 (可选)
    :return: Issues列表
    """
    try:
        issues = repo.get_issues(state=state, labels=labels)
        return issues
    except Exception as e:
        print(f"获取Issues失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

issues_list = []
count = 8
issues = get_issues(repo, state="closed", labels=[])
print(type(issues))

for issue in issues:
    if count >= max_issues:
        break
    if "pull_request" in issue.raw_data:
        print(f"跳过PR: {issue.html_url}")
        continue
    issues_list.append(issue.raw_data)
    count += 1
    print(f"已处理 {count} 个issue")
save_data(issues_list, "issues_test.json")