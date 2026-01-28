from github import Github
import github.Auth
import nltk
import re
import requests
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import os
import base64
import json

# 确保nltk数据已下载
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

# 跳过punkt资源的检查，因为punkt_tab可以替代它
# 避免punkt资源文件损坏导致的错误
try:
    # 尝试使用punkt_tab进行分词
    from nltk.tokenize import word_tokenize
    test_text = "This is a test."
    word_tokenize(test_text)
except Exception as e:
    print(f"分词初始化失败，但将继续执行: {str(e)}")

class GitHubCollector:
    def __init__(self, access_token):
        """
        初始化GitHubCollector实例
        :param access_token: GitHub个人访问令牌
        """
        self.access_token = access_token
        # 使用新的认证方式
        auth = github.Auth.Token(access_token)
        self.g = Github(auth=auth)
        self.stop_words = set(stopwords.words('english'))
        # 定义源代码文件扩展名
        self.source_code_extensions = {
            '.py', '.java', '.c', '.cpp', '.h', '.hpp', '.js', '.ts', '.jsx', '.tsx',
            '.html', '.css', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala',
            '.sql', '.sh', '.md', '.txt'
        }
    
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
            return None
    
    def get_issues(self, repo, state="all", labels=None):
        """
        获取仓库的Issues
        :param repo: 仓库对象
        :param state: Issues状态 (open, closed, all)
        :param labels: 标签列表，用于过滤
        :return: Issues列表
        """
        try:
            if labels:
                issues = repo.get_issues(state=state, labels=labels)
            else:
                issues = repo.get_issues(state=state)
            
            issues_list = []
            for issue in issues:
                try:
                    issues_list.append({
                        "id": issue.id,
                        "number": issue.number,
                        "title": issue.title or "",
                        "body": issue.body or "",
                        "state": issue.state,
                        "created_at": issue.created_at,
                        "updated_at": issue.updated_at,
                        "labels": [label.name for label in issue.labels],
                        "user": issue.user.login if issue.user else "",
                        "assignee": issue.assignee.login if issue.assignee else None
                    })
                except Exception as item_error:
                    print(f"处理Issue #{issue.number} 时出错: {str(item_error)}")
                    continue
            return issues_list
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
        :return: Commits列表
        """
        try:
            # 限制获取的Commits数量，避免API速率限制
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
            
            commits_list = []
            count = 0
            max_commits = 1000  # 限制最多获取1000个Commits
            
            for commit in commits:
                try:
                    # 检查是否超过限制
                    if count >= max_commits:
                        print(f"已达到Commits获取限制 ({max_commits}个)")
                        break
                    
                    commit_data = {
                        "sha": commit.sha,
                        "message": commit.commit.message or "",
                        "url": commit.html_url
                    }
                    
                    # 安全获取作者信息
                    if commit.commit.author:
                        commit_data["author"] = commit.commit.author.name or ""
                        commit_data["email"] = commit.commit.author.email or ""
                        commit_data["date"] = commit.commit.author.date
                    else:
                        commit_data["author"] = None
                        commit_data["email"] = None
                        commit_data["date"] = None
                    
                    # 安全获取提交者信息
                    if commit.commit.committer:
                        commit_data["committer"] = commit.commit.committer.name or ""
                        commit_data["committer_email"] = commit.commit.committer.email or ""
                        commit_data["committer_date"] = commit.commit.committer.date
                    else:
                        commit_data["committer"] = None
                        commit_data["committer_email"] = None
                        commit_data["committer_date"] = None
                    
                    commits_list.append(commit_data)
                    count += 1
                except Exception as item_error:
                    print(f"处理Commit {commit.sha[:7]} 时出错: {str(item_error)}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            return commits_list
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
        :return: Pull Requests列表
        """
        try:
            pulls = repo.get_pulls(state=state)
            pulls_list = []
            for pr in pulls:
                pulls_list.append({
                    "id": pr.id,
                    "number": pr.number,
                    "title": pr.title,
                    "body": pr.body,
                    "state": pr.state,
                    "created_at": pr.created_at,
                    "updated_at": pr.updated_at,
                    "merged_at": pr.merged_at,
                    "user": pr.user.login,
                    "assignee": pr.assignee.login if pr.assignee else None,
                    "labels": [label.name for label in pr.labels],
                    "head": pr.head.ref,
                    "base": pr.base.ref,
                    "merged": pr.merged,
                    "merge_commit_sha": pr.merge_commit_sha
                })
            return pulls_list
        except Exception as e:
            print(f"获取Pull Requests失败: {str(e)}")
            return []
    
    def get_files(self, repo, path="."):
        """
        递归获取仓库中的所有文件
        :param repo: 仓库对象
        :param path: 起始路径
        :return: 文件列表
        """
        try:
            contents = repo.get_contents(path)
            files_list = []
            
            for content in contents:
                if content.type == "dir":
                    # 递归处理子目录
                    files_list.extend(self.get_files(repo, content.path))
                else:
                    # 处理文件
                    files_list.append({
                        "path": content.path,
                        "name": content.name,
                        "type": content.type,
                        "size": content.size,
                        "download_url": content.download_url
                    })
            return files_list
        except Exception as e:
            print(f"获取文件失败: {str(e)}")
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
                return base64.b64decode(content.content).decode('utf-8', errors='replace')
            else:
                return content.content
        except Exception as e:
            print(f"获取文件内容失败: {str(e)}")
            return None
    
    def preprocess_text(self, text):
        """
        预处理文本，包括去噪、停用词过滤和格式统一
        :param text: 原始文本
        :return: 预处理后的文本
        """
        if not text:
            return ""
        
        # 1. 去除特殊符号和链接
        # 去除链接
        text = re.sub(r'http\S+', '', text)
        text = re.sub(r'https\S+', '', text)
        # 去除特殊符号，保留字母、数字和空格
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        
        # 2. 转换为小写
        text = text.lower()
        
        # 3. 分词
        tokens = word_tokenize(text)
        
        # 4. 过滤停用词
        filtered_tokens = [token for token in tokens if token not in self.stop_words]
        
        # 5. 格式统一，合并为空格分隔的字符串
        processed_text = ' '.join(filtered_tokens)
        
        return processed_text
    
    def preprocess_issues(self, issues):
        """
        预处理Issues列表
        :param issues: Issues列表
        :return: 预处理后的Issues列表
        """
        processed_issues = []
        for issue in issues:
            processed_issue = issue.copy()
            processed_issue['title'] = self.preprocess_text(issue['title'])
            processed_issue['body'] = self.preprocess_text(issue['body'])
            processed_issues.append(processed_issue)
        return processed_issues
    
    def preprocess_commits(self, commits):
        """
        预处理Commits列表
        :param commits: Commits列表
        :return: 预处理后的Commits列表
        """
        processed_commits = []
        for commit in commits:
            processed_commit = commit.copy()
            processed_commit['message'] = self.preprocess_text(commit['message'])
            processed_commits.append(processed_commit)
        return processed_commits
    
    def preprocess_pull_requests(self, prs):
        """
        预处理Pull Requests列表
        :param prs: Pull Requests列表
        :return: 预处理后的Pull Requests列表
        """
        processed_prs = []
        for pr in prs:
            processed_pr = pr.copy()
            processed_pr['title'] = self.preprocess_text(pr['title'])
            processed_pr['body'] = self.preprocess_text(pr['body'])
            processed_prs.append(processed_pr)
        return processed_prs
    
    def filter_source_files(self, files):
        """
        过滤文件列表，保留源代码文件
        :param files: 文件列表
        :return: 过滤后的源代码文件列表
        """
        source_files = []
        for file in files:
            # 获取文件扩展名
            _, ext = os.path.splitext(file['name'])
            # 检查是否为源代码文件
            if ext in self.source_code_extensions:
                source_files.append(file)
        return source_files
    
    def is_source_file(self, file_path):
        """
        检查指定文件是否为源代码文件
        :param file_path: 文件路径
        :return: 是否为源代码文件
        """
        _, ext = os.path.splitext(file_path)
        return ext in self.source_code_extensions

def load_config(config_file="config.json"):
    """
    从配置文件加载配置信息
    :param config_file: 配置文件路径
    :return: 配置字典
    """
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"加载配置文件失败: {str(e)}")
        return None

def save_data(data, file_path):
    """
    保存数据到指定文件
    :param data: 要保存的数据
    :param file_path: 文件路径
    """
    try:
        # 处理路径，确保使用正确的路径分隔符
        file_path = os.path.normpath(file_path)
        
        # 确保目录存在
        dir_path = os.path.dirname(file_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        
        # 保存数据
        with open(file_path, 'w', encoding='utf-8') as f:
            # 自定义序列化函数，处理复杂类型
            def default_serializer(obj):
                if hasattr(obj, '__dict__'):
                    return obj.__dict__
                elif isinstance(obj, (bytes, bytearray)):
                    return obj.decode('utf-8', errors='replace')
                else:
                    return str(obj)
            
            json.dump(data, f, ensure_ascii=False, indent=2, default=default_serializer)
        print(f"数据保存成功: {file_path}")
    except Exception as e:
        print(f"保存数据失败: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """
    主函数，整合各功能模块
    """
    # 从配置文件加载配置
    config = load_config()
    if not config:
        print("无法加载配置文件，请检查config.json文件是否存在且格式正确")
        return
    
    # 从配置中获取信息
    access_token = config.get("token")
    repo_owner = config.get("owner")
    repo_name = config.get("repo")
    
    # 验证配置信息
    if not all([access_token, repo_owner, repo_name]):
        print("配置信息不完整，请检查config.json文件中的token、owner和repo字段")
        return
    
    print(f"从配置文件加载信息成功: {repo_owner}/{repo_name}")
    
    # 初始化GitHubCollector实例
    collector = GitHubCollector(access_token)
    
    # 获取仓库对象
    repo = collector.get_repo(repo_owner, repo_name)
    if not repo:
        print("无法获取仓库，请检查输入信息和访问令牌权限")
        return
    
    print(f"成功获取仓库: {repo.name}")
    
    # 数据保存目录
    data_dir = f"data/{repo_name}"
    
    # 1. 采集Issues数据
    print("\n开始采集Issues数据...")
    issues = collector.get_issues(repo, state="all")
    print(f"采集到 {len(issues)} 个Issues")
    
    # 预处理Issues数据
    processed_issues = collector.preprocess_issues(issues)
    print(f"预处理完成 {len(processed_issues)} 个Issues")
    
    # 保存Issues数据
    save_data(issues, f"{data_dir}/issues_raw.json")
    save_data(processed_issues, f"{data_dir}/issues_processed.json")
    
    # 2. 采集Commits数据
    print("\n开始采集Commits数据...")
    commits = collector.get_commits(repo)
    print(f"采集到 {len(commits)} 个Commits")
    
    # 预处理Commits数据
    processed_commits = collector.preprocess_commits(commits)
    print(f"预处理完成 {len(processed_commits)} 个Commits")
    
    # 保存Commits数据
    save_data(commits, f"{data_dir}/commits_raw.json")
    save_data(processed_commits, f"{data_dir}/commits_processed.json")
    
    # 3. 采集Pull Requests数据
    print("\n开始采集Pull Requests数据...")
    prs = collector.get_pull_requests(repo, state="all")
    print(f"采集到 {len(prs)} 个Pull Requests")
    
    # 预处理Pull Requests数据
    processed_prs = collector.preprocess_pull_requests(prs)
    print(f"预处理完成 {len(processed_prs)} 个Pull Requests")
    
    # 保存Pull Requests数据
    save_data(prs, f"{data_dir}/pull_requests_raw.json")
    save_data(processed_prs, f"{data_dir}/pull_requests_processed.json")
    
    # 4. 采集文件数据
    print("\n开始采集文件数据...")
    files = collector.get_files(repo)
    print(f"采集到 {len(files)} 个文件")
    
    # 过滤源代码文件
    source_files = collector.filter_source_files(files)
    print(f"过滤后得到 {len(source_files)} 个源代码文件")
    
    # 保存文件数据
    save_data(files, f"{data_dir}/files_raw.json")
    save_data(source_files, f"{data_dir}/files_source.json")
    
    # 打印部分源代码文件路径
    print("\n部分源代码文件路径:")
    for file in source_files[:10]:  # 只打印前10个
        print(f"- {file['path']}")
    
    if len(source_files) > 10:
        print(f"... 等 {len(source_files) - 10} 个文件")
    
    print("\n数据采集、预处理和保存完成！")

if __name__ == "__main__":
    main()
