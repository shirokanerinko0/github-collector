import javalang
import json
import os

def collect_method_invocations(method_node):
    """
    收集方法体中的所有方法调用
    :param method_node: 方法节点
    :return: 方法调用名称列表
    """
    invocations = []
    
    # 检查方法是否有方法体
    if hasattr(method_node, 'body') and method_node.body:
        # 定义一个辅助函数来遍历节点
        def traverse(node):
            if isinstance(node, javalang.tree.MethodInvocation):
                # 提取方法调用名称
                invocations.append(node.member)
            # 处理列表节点
            if isinstance(node, list):
                for item in node:
                    traverse(item)
            # 处理其他可迭代节点
            elif hasattr(node, '__dict__'):
                # 遍历节点的所有属性
                for attr_name, attr_value in node.__dict__.items():
                    # 跳过一些不需要的属性
                    if attr_name.startswith('_'):
                        continue
                    # 递归遍历属性值
                    if isinstance(attr_value, (list, dict)):
                        if isinstance(attr_value, list):
                            for item in attr_value:
                                traverse(item)
                        elif isinstance(attr_value, dict):
                            for value in attr_value.values():
                                traverse(value)
                    else:
                        # 尝试直接遍历属性值
                        try:
                            traverse(attr_value)
                        except:
                            pass
        
        # 开始遍历方法体
        traverse(method_node.body)
    
    # 去重
    invocations = list(set(invocations))
    print(f"Method: {method_node.name}, Called functions: {invocations}")
    return invocations

def get_method_comment(method_node):
    """
    获取方法的注释
    :param method_node: 方法节点
    :return: 注释文本
    """
    # 尝试从不同位置获取注释
    if hasattr(method_node, 'comment') and method_node.comment:
        return method_node.comment
    elif hasattr(method_node, 'documentation') and method_node.documentation:
        return method_node.documentation
    else:
        return ""

def analyze_java_code(code):
    """
    分析Java代码结构，提取函数信息
    :param code: Java代码字符串
    :return: 包含类和函数信息的字典
    """
    tree = javalang.parse.parse(code)
    
    # 保存完整的代码到tree对象，以便后续使用
    tree.code = code
    
    result = {
        "classes": []
    }
    
    def get_node_code(node, code):
        """
        获取节点的原始代码
        :param node: AST节点
        :param code: 完整的Java代码字符串
        :return: 节点的原始代码
        """
        if not node or not hasattr(node, 'position') or not node.position:
            return ""

        try:
            # 1. 对整个代码进行Token化
            tokens = list(javalang.tokenizer.tokenize(code))
            
            # 2. 找到对应节点的起始Token索引
            start_token_index = -1
            for i, token in enumerate(tokens):
                # node.position.line 是从1开始的，token.position.line 也是
                if hasattr(token, 'position') and token.position:
                    if token.position.line == node.position.line and token.position.column == node.position.column:
                        start_token_index = i
                        break
                        
            if start_token_index == -1:
                return "" # 没找到对应的起始token

            # 3. 寻找结束Token（基于大括号平衡）
            balance = 0
            end_token_index = -1
            found_start_brace = False
            
            # 从起始token开始往后找
            for i in range(start_token_index, len(tokens)):
                token = tokens[i]
                
                # 只处理分隔符类型的Token
                if isinstance(token, javalang.tokenizer.Separator):
                    if token.value == '{':
                        balance += 1
                        found_start_brace = True
                    elif token.value == '}':
                        balance -= 1
                
                # 如果已经开始过代码块，且平衡归零，说明找到了结束位置
                if found_start_brace and balance == 0:
                    end_token_index = i
                    break
                    
            if end_token_index == -1:
                # 可能是没有代码体的方法（如接口方法或抽象方法），直接取到分号
                for i in range(start_token_index, len(tokens)):
                    if tokens[i].value == ';':
                        end_token_index = i
                        break
                        
            if end_token_index == -1:
                return "" # 无法确定结束位置

            # 4. 根据Token的位置计算在原始字符串中的截取范围
            # 辅助函数：将行列转换为字符串索引
            def get_index(line, column, code_lines):
                # line从1开始，column从1开始
                if line > len(code_lines):
                    return len(code)
                
                # 计算前几行的总长度
                current_index = 0
                for l in range(line - 1):
                    current_index += len(code_lines[l]) + 1 # +1 是换行符（假设是\n）
                    
                current_index += (column - 1)
                return current_index

            lines = code.split('\n')
            
            # 起始位置：节点的开始
            start_token = tokens[start_token_index]
            if hasattr(start_token, 'position') and start_token.position:
                start_idx = get_index(start_token.position.line, start_token.position.column, lines)
            else:
                return ""
            
            # 结束位置：结束Token的末尾
            end_token = tokens[end_token_index]
            if hasattr(end_token, 'position') and end_token.position:
                # end_idx 是结束token的起始位置 + 它的长度
                end_token_start_idx = get_index(end_token.position.line, end_token.position.column, lines)
                end_idx = end_token_start_idx + len(end_token.value)
            else:
                return ""

            return code[start_idx:end_idx]
        except Exception as e:
            # 如果出现任何错误，返回空字符串
            print(f"提取源码时出错: {e}")
            return ""

    def process_class(node, depth=0):
        """
        处理类节点，包括内部类
        :param node: 类节点
        :param depth: 当前递归深度
        :return: 类信息字典
        """
        # 深度限制，避免递归过深
        if depth > 10:
            return None
        
        # 确保node是类声明节点
        if not isinstance(node, javalang.tree.ClassDeclaration):
            return None
        
        # 获取完整的Java代码
        code = tree.code if hasattr(tree, 'code') else ""
        
        class_info = {
            "name": node.name,
            "modifiers": list(node.modifiers) if hasattr(node, 'modifiers') else [],
            "methods": [],
            "inner_classes": [],
            "original_code": get_node_code(node, code)
        }
        
        # 查找该类下的所有方法和内部类
        try:
            # 使用更安全的方式遍历类成员
            if hasattr(node, 'body') and node.body:
                for member in node.body:
                    if isinstance(member, (javalang.tree.MethodDeclaration, javalang.tree.ConstructorDeclaration)):
                        # 解析方法或构造函数信息
                        is_constructor = isinstance(member, javalang.tree.ConstructorDeclaration)
                        
                        method_info = {
                            "modifiers": list(member.modifiers) if hasattr(member, 'modifiers') else [],
                            "comments": get_method_comment(member),
                            "called_functions": collect_method_invocations(member),
                            "name": member.name,
                            "return_type": "void" if is_constructor else get_type_name(member.return_type),
                            "parameters": [],
                            "original_code": get_node_code(member, code),
                            "is_constructor": is_constructor
                        }
                        
                        # 解析参数信息
                        for param in member.parameters:
                            param_info = {
                                "type": get_type_name(param.type),
                                "name": param.name
                            }
                            method_info["parameters"].append(param_info)
                        
                        class_info["methods"].append(method_info)
                    elif isinstance(member, javalang.tree.ClassDeclaration):
                        # 只处理不同名的内部类（java不允许内部类和外部类同名）
                        if member.name != node.name:
                            # 处理内部类，增加深度
                            inner_class_info = process_class(member, depth + 1)
                            if inner_class_info:
                                class_info["inner_classes"].append(inner_class_info)
        except Exception as e:
            print(f"处理类节点时出错: {e}")
        
        return class_info
    
    # 遍历所有顶级类
    for path, node in tree:
        if isinstance(node, javalang.tree.ClassDeclaration):
            # 直接处理类声明，让process_class函数处理内部类的问题
            class_info = process_class(node)
            if class_info:
                # 确保只添加真正的顶级类（没有父类路径）
                # 检查path是否表示顶级类
                if len(path) == 1 or not any(isinstance(p, javalang.tree.ClassDeclaration) for p in path):
                    result["classes"].append(class_info)
    
    return result

def get_type_name(type_node):
    """
    获取类型的字符串表示
    :param type_node: 类型节点
    :return: 类型名称字符串
    """
    if type_node is None:
        return "void"
    elif hasattr(type_node, 'name'):
        return type_node.name
    elif hasattr(type_node, 'element_type'):
        # 处理数组类型
        return f"{get_type_name(type_node.element_type)}[]"
    else:
        return str(type_node)

def save_to_json(data, output_file):
    """
    将分析结果保存为JSON文件
    :param data: 分析结果数据
    :param output_file: 输出文件路径
    """
    # 确保输出目录存在
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"分析结果已保存到: {output_file}")

# 测试代码
code = """
public class Test {
    private int userId;

    /**
     * 用户登录方法
     * @param userName 用户名
     */
    public void loginUser(String userName) {
        checkPassword(userName);
        validateInput(userName);
    }

    /**
     * 检查密码
     * @param name 用户名
     */
    private void checkPassword(String name) {
        validateInput(name);
    }
    
    /**
     * 获取用户信息
     * @param id 用户ID
     * @param format 格式
     * @return 用户信息
     */
    public int getUserInfo(int id, String format) {
        validateInput(format);
        return 0;
    }
    
    /**
     * 获取名称列表
     * @return 名称列表
     */
    private List<String> getNames() {
        return new ArrayList<>();
    }
    
    /**
     * 验证输入
     * @param input 输入字符串
     */
    private void validateInput(String input) {
        // 验证逻辑
    }
}
"""

# 从文件读取Java代码进行分析（可选功能）
def analyze_java_file(file_path):
    """
    从文件读取Java代码并分析
    :param file_path: Java文件路径
    :return: 分析结果
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
    return analyze_java_code(code)

# 测试分析Java文件
if __name__ == "__main__":
    # 分析字符串代码
    analysis_result = analyze_java_code(code)
    
    # 打印分析结果
    print("=== Java代码分析结果 ===")
    print(json.dumps(analysis_result, ensure_ascii=False, indent=2))
    
    # 保存为JSON文件
    save_to_json(analysis_result, "output/java_method_analysis.json")
    
    # 分析Java测试文件
    test_files = [
        "src/JavaCodeAnalyzer/javacodetest/SimpleTest.java",
        "src/JavaCodeAnalyzer/javacodetest/ComplexTest.java",
        "src/JavaCodeAnalyzer/javacodetest/InterfaceTest.java",
        "src/JavaCodeAnalyzer/javacodetest/InnerClassTest.java",
        "src/JavaCodeAnalyzer/javacodetest/MultipleClassesTest.java",
        "src/JavaCodeAnalyzer/javacodetest/NestedInnerClassTest.java",
        "src/JavaCodeAnalyzer/javacodetest/CommentBraceTest.java"
    ]
    
    print("\n=== 分析Java测试文件 ===")
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\n分析文件: {test_file}")
            file_result = analyze_java_file(test_file)
            output_file = f"output/{os.path.basename(test_file).replace('.java', '_analysis.json')}"
            save_to_json(file_result, output_file)
        else:
            print(f"文件不存在: {test_file}")
