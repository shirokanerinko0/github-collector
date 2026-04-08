import os
import sys
import shutil
import subprocess

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.utils.utils import load_config
from file_operations.main import clean_repository
CONFIG = load_config()


def download_repository(owner=None, repo=None, target_dir=None, force=False, clean=True):
    """
    从GitHub下载指定仓库到目标目录
    
    Args:
        owner (str, optional): 仓库所有者，如果为None则从config读取
        repo (str, optional): 仓库名称，如果为None则从config读取
        target_dir (str, optional): 目标目录，如果为None则使用 data/{repo}/origin_src
        force (bool): 是否强制重新下载，即使目录已存在
        clean (bool): 下载后是否清理非代码文件和空文件夹
    
    Returns:
        str: 下载的仓库目录路径
    """
    
    if owner is None:
        owner = CONFIG.get("owner")
    if repo is None:
        repo = CONFIG.get("repo")
    if target_dir is None:
        target_dir = os.path.join("data", repo, "origin_src")
    
    print(f"准备下载仓库: {owner}/{repo}")
    print(f"目标目录: {target_dir}")
    
    # 检查目标目录是否已存在
    if os.path.exists(target_dir):
        if force:
            print(f"目标目录已存在，正在删除...")
            shutil.rmtree(target_dir)
        else:
            print(f"目标目录已存在，跳过下载")
            return target_dir
    
    # 确保父目录存在
    os.makedirs(os.path.dirname(target_dir), exist_ok=True)
    
    # 构建GitHub仓库URL
    token = CONFIG.get("token", "")
    if token:
        repo_url = f"https://{token}@github.com/{owner}/{repo}.git"
    else:
        repo_url = f"https://github.com/{owner}/{repo}.git"
    
    print(f"正在克隆仓库: {repo_url}")
    
    try:
        # 使用 git clone 命令克隆仓库
        result = subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, target_dir],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("仓库下载成功!")
            if clean:
                print("\n开始清理仓库...")
                clean_repository(target_dir)
            return target_dir
        else:
            print(f"仓库下载失败: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"下载仓库时出错: {e}")
        return None


def download_without_git(owner=None, repo=None, target_dir=None, force=False, clean=True):
    """
    不使用git，通过GitHub API下载仓库（备选方案）
    
    Args:
        owner (str, optional): 仓库所有者，如果为None则从config读取
        repo (str, optional): 仓库名称，如果为None则从config读取
        target_dir (str, optional): 目标目录，如果为None则使用 data/{repo}/origin_src
        force (bool): 是否强制重新下载，即使目录已存在
        clean (bool): 下载后是否清理非代码文件和空文件夹
    
    Returns:
        str: 下载的仓库目录路径
    """
    import requests
    import zipfile
    import io
    
    config = load_config()
    
    if owner is None:
        owner = config.get("owner")
    if repo is None:
        repo = config.get("repo")
    if target_dir is None:
        target_dir = os.path.join("data", repo, "origin_src")
    
    print(f"准备下载仓库: {owner}/{repo} (使用zip方式)")
    print(f"目标目录: {target_dir}")
    
    # 检查目标目录是否已存在
    if os.path.exists(target_dir):
        if force:
            print(f"目标目录已存在，正在删除...")
            shutil.rmtree(target_dir)
        else:
            print(f"目标目录已存在，跳过下载")
            return target_dir
    
    # 确保父目录存在
    os.makedirs(os.path.dirname(target_dir), exist_ok=True)
    
    # 下载zip文件
    zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{CONFIG['main_branch']}.zip"
    print(f"正在下载: {zip_url}")
    
    try:
        response = requests.get(zip_url)
        response.raise_for_status()
        
        # 解压到临时目录
        temp_dir = target_dir + "_temp"
        with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
            zf.extractall(temp_dir)
        
        # 找到解压后的实际目录（通常是 repo-master）
        extracted_dirs = os.listdir(temp_dir)
        if len(extracted_dirs) == 1:
            extracted_dir = os.path.join(temp_dir, extracted_dirs[0])
            # 移动到目标目录
            shutil.move(extracted_dir, target_dir)
            # 删除临时目录
            shutil.rmtree(temp_dir)
            print("仓库下载成功!")
            if clean:
                print("\n开始清理仓库...")
                clean_repository(target_dir)
            return target_dir
        else:
            print("解压后目录结构异常")
            shutil.rmtree(temp_dir)
            return None
            
    except Exception as e:
        print(f"下载仓库时出错: {e}")
        return None


def download_repository_main():
    # 使用zip方式下载仓库
    result = download_without_git(force=False, clean=True)
    
    if result:
        print(f"\n仓库已保存到: {result}")
    else:
        print("\n仓库下载失败")
        sys.exit(1)

if __name__ == "__main__":
    print("=" * 60)
    print("GitHub仓库下载工具")
    print("=" * 60)
    download_repository_main()

