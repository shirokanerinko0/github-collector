import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.JavaCodeAnalyzer.code_identifier_processor import CodeIdentifierProcessor

def process_all_json_files(input_dir, output_dir=None):
    """
    批量处理目录下的所有 JSON 文件
    
    Args:
        input_dir (str): 输入目录路径
        output_dir (str, optional): 输出目录路径
        
    Returns:
        dict: 处理结果统计
    """
    if not os.path.exists(input_dir):
        print(f"错误: 输入目录不存在: {input_dir}")
        return {"total": 0, "success": 0, "failed": 0}
    
    # 初始化处理器
    processor = CodeIdentifierProcessor()
    
    # 确定输出目录
    if not output_dir:
        output_dir = os.path.join(input_dir, "enhanced")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 统计信息
    stats = {"total": 0, "success": 0, "failed": 0}
    
    # 遍历目录下的所有文件
    print(f"开始处理目录: {input_dir}")
    print(f"增强结果将保存到: {output_dir}")
    print()
    
    for filename in os.listdir(input_dir):
        if filename.endswith(".json") and not filename.endswith("_enhanced.json"):
            input_file = os.path.join(input_dir, filename)
            output_file = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}_enhanced.json")
            
            print(f"处理文件: {filename}")
            stats["total"] += 1
            
            # 处理文件
            success = processor.process_json_file(input_file, output_file)
            if success:
                stats["success"] += 1
            else:
                stats["failed"] += 1
            
            print()
    
    # 打印统计信息
    print("=== 处理完成 ===")
    print(f"总文件数: {stats['total']}")
    print(f"成功处理: {stats['success']}")
    print(f"处理失败: {stats['failed']}")
    
    return stats

if __name__ == "__main__":
    # 默认输入目录为 output
    input_dir = "output"
    
    # 如果命令行提供了输入目录，则使用命令行参数
    if len(sys.argv) > 1:
        input_dir = sys.argv[1]
    
    # 处理所有 JSON 文件
    process_all_json_files(input_dir)
