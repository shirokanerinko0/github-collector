import os

# 目标目录
target_dir = "d:\\OneDrive\\graduation_project\\TRae\\file_operations\\repo\\guava-master"
file_extensions = ('.java',)
def delete_non_java_files(directory):
    """删除目录及其子目录中的非代码文件"""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if not file.endswith(file_extensions):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"已删除: {file_path}")
                except Exception as e:
                    print(f"删除文件失败 {file_path}: {e}")

def delete_empty_dirs(directory):
    """递归删除空文件夹"""
    # 先递归处理子目录
    for root, dirs, files in os.walk(directory, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if not os.listdir(dir_path):  # 检查目录是否为空
                try:
                    os.rmdir(dir_path)
                    print(f"已删除空目录: {dir_path}")
                except Exception as e:
                    print(f"删除空目录失败 {dir_path}: {e}")

if __name__ == "__main__":
    print(f"开始清理目录: {target_dir}")
    print("\n1. 删除非Java文件...")
    delete_non_java_files(target_dir)
    print("\n2. 删除空文件夹...")
    delete_empty_dirs(target_dir)
    print("\n清理完成！")