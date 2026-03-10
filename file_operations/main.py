import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.utils.utils import load_config


def delete_non_code_files(directory, file_extensions=None):
    """
    删除目录及其子目录中的非代码文件
    
    Args:
        directory (str): 要清理的目录
        file_extensions (tuple, optional): 要保留的文件扩展名，如果为None则从config读取
    """
    config = load_config()
    
    if file_extensions is None:
        file_extensions = tuple(config.get("source_code_extensions", [".java"]))
    
    print(f"\n1. 删除非代码文件 (保留: {file_extensions})...")
    
    deleted_count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if not file.endswith(file_extensions):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    deleted_count += 1
                    if deleted_count % 100 == 0:
                        print(f"已删除 {deleted_count} 个文件...")
                except Exception as e:
                    print(f"删除文件失败 {file_path}: {e}")
    
    print(f"共删除 {deleted_count} 个非代码文件")


def delete_empty_dirs(directory):
    """
    递归删除空文件夹
    
    Args:
        directory (str): 要清理的目录
    """
    print("\n2. 删除空文件夹...")
    
    deleted_count = 0
    # 先递归处理子目录
    for root, dirs, files in os.walk(directory, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if os.path.exists(dir_path) and not os.listdir(dir_path):  # 检查目录是否为空
                try:
                    os.rmdir(dir_path)
                    deleted_count += 1
                    if deleted_count % 50 == 0:
                        print(f"已删除 {deleted_count} 个空目录...")
                except Exception as e:
                    print(f"删除空目录失败 {dir_path}: {e}")
    
    print(f"共删除 {deleted_count} 个空目录")


def clean_repository(directory, file_extensions=None):
    """
    清理仓库：删除非代码文件和空文件夹
    
    Args:
        directory (str): 要清理的目录
        file_extensions (tuple, optional): 要保留的文件扩展名
    
    Returns:
        bool: 清理是否成功
    """
    if not os.path.exists(directory):
        print(f"目录不存在: {directory}")
        return False
    
    print(f"开始清理目录: {directory}")
    print("=" * 60)
    
    try:
        delete_non_code_files(directory, file_extensions)
        delete_empty_dirs(directory)
        print("\n" + "=" * 60)
        print("清理完成！")
        return True
    except Exception as e:
        print(f"\n清理失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # 目标目录
    target_dir = "d:\\OneDrive\\graduation_project\\TRae\\file_operations\\repo\\guava-master"
    clean_repository(target_dir)
