import tree_sitter
import tree_sitter_java
import json
import os,sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.utils.utils import load_config
CONFIG = load_config()
DEBUG = False
re_analyze_code = CONFIG["re_analyze_code"]

class JavaCodeAnalyzer:
    def __init__(self):
        """
        初始化 Tree-sitter 解析器
        """
        try:
            # 初始化 Parser
            self.parser = tree_sitter.Parser()
            
            # 加载 Java 语言定义
            # 注意：不同版本的 tree-sitter 库加载方式略有不同，这里使用最新标准
            java_lang = tree_sitter.Language(tree_sitter_java.language())
            self.parser.language = java_lang
            
        except Exception as e:
            print(f"Error: 初始化 Tree-sitter 失败。请确保已安装 tree-sitter 和 tree-sitter-java。\n{e}")
            raise

    def analyze_code(self, source_code):
        """
        分析 Java 代码字符串
        """
        if not source_code:
            return {"classes": [], "source_code": ""}

        # 【核心修复】：将源码转换为 UTF-8 字节
        # Tree-sitter 的 start_byte/end_byte 是基于字节的，直接切片 Unicode 字符串会出错（特别是包含中文时）
        self.source_bytes = bytes(source_code, "utf8")
        
        # 解析代码生成语法树
        tree = self.parser.parse(self.source_bytes)
        
        result = {
            "classes": [],
            "source_code": source_code
        }

        # 遍历根节点下的所有 class_declaration
        # 使用 cursor 遍历或者简单的递归查找
        root_node = tree.root_node
        self._find_and_process_classes(root_node, result["classes"])
        
        return result

    def _get_text(self, node):
        """
        【工具函数】从节点提取源码文本
        正确处理字节切片，防止中文乱码
        """
        if not node:
            return ""
        # 使用字节切片，然后解码回字符串
        return self.source_bytes[node.start_byte : node.end_byte].decode("utf8")

    def _find_and_process_classes(self, node, class_list, depth=0):
        """
        递归查找并处理类声明
        """
        if depth > 10: return # 防止过深

        # 遍历当前层级的子节点
        for child in node.children:
            if child.type == 'class_declaration':
                class_info = self._process_class_node(child)
                if class_info:
                    class_list.append(class_info)
            
            # 如果不是类定义，但可能包含类（比如模块定义等），可以在这里扩展
            # 对于内部类，我们会在 _process_class_node 内部递归处理，所以这里不需要深层递归

    def _process_class_node(self, class_node):
        """
        处理单个类节点
        """
        # 1. 获取类名 (使用 field 'name')
        name_node = class_node.child_by_field_name('name')
        class_name = self._get_text(name_node)
        if not class_name: return None

        # 2. 获取修饰符 (查找 modifiers 类型的子节点)
        modifiers = []
        for child in class_node.children:
            if child.type == "modifiers":
                for mod in child.children:
                    # 跳过注解类型的节点，只添加真正的修饰符
                    if mod.type not in ['marker_annotation', 'annotation']:
                        modifiers.append(self._get_text(mod))

        # 5. 提取注解
        annotations = []
        # 遍历 class_node 的所有子节点
        for child in class_node.children:
            # 如果是 modifiers 节点，检查其内部子节点
            if child.type == 'modifiers':
                for mod_child in child.children:
                    # 检查是否是注解（包括 marker_annotation 和 annotation）
                    if mod_child.type in ['marker_annotation', 'annotation']:
                        annotations.append(self._get_text(mod_child))

        # 6. 提取类继承关系和接口实现关系
        extends = []
        implements = []
        
        # 遍历 class_node 的所有子节点
        for child in class_node.children:
            # 查找 superclass 节点（父类）
            if child.type == 'superclass':
                # 提取父类名称，移除 'extends ' 前缀
                superclass_text = self._get_text(child)
                if superclass_text.startswith('extends '):
                    extends.append(superclass_text[8:].strip())
                else:
                    extends.append(superclass_text.strip())
            # 查找 super_interfaces 节点（实现的接口）
            elif child.type == 'super_interfaces':
                # 遍历 super_interfaces 节点的子节点，提取接口名称
                for interface_child in child.children:
                    if interface_child.type != 'comma' and interface_child.type != 'implements':  # 跳过逗号和 implements 关键字
                        interface_text = self._get_text(interface_child).strip()
                        if interface_text:
                            # 分割多个接口名（如果有逗号分隔）
                            for interface_name in interface_text.split(','):
                                trimmed_name = interface_name.strip()
                                if trimmed_name:
                                    implements.append(trimmed_name)

        class_info = {
            "name": class_name,
            "modifiers": modifiers,
            "annotations": annotations,
            "extends": extends,
            "implements": implements,
            "methods": [],
            "inner_classes": [],
            "original_code": self._get_text(class_node)
        }
        
        # 获取类的注释
        class_comment = self._get_comments(class_node)
        
        # 生成类的所有代码片段变体
        class_info["code_snippets"] = {}
        
        # 原始类代码 (default)
        class_info["code_snippets"]["default"] = class_info["original_code"]
        
        # 类+注释 (CD: class with docstring)
        if class_comment:
            class_info["code_snippets"]["CD"] = f"{class_comment}\n{class_info['original_code']}"
        else:
            class_info["code_snippets"]["CD"] = class_info["original_code"]
        
        # 设置默认 enriched_code（使用原始代码作为默认值）
        class_info["enriched_code"] = class_info["code_snippets"]["default"]

        # 处理类体 (class_body)
        body_node = class_node.child_by_field_name('body')
        if body_node:
            for member in body_node.children:
                if member.type == 'method_declaration':
                    method_info = self._process_method_node(member, is_constructor=False, class_info=class_info)
                    class_info["methods"].append(method_info)
                
                elif member.type == 'constructor_declaration':
                    method_info = self._process_method_node(member, is_constructor=True, class_info=class_info)
                    class_info["methods"].append(method_info)
                
                elif member.type == 'class_declaration':
                    # 递归处理内部类
                    inner_class = self._process_class_node(member)
                    if inner_class:
                        class_info["inner_classes"].append(inner_class)
        
        # 添加类的最终 enriched_code（使用原始代码作为默认值）
        class_info["enriched_code"] = class_info["code_snippets"].get("default", class_info["original_code"])

        return class_info

    def _process_method_node(self, method_node, is_constructor=False, class_info=None):
        """
        处理方法或构造函数节点
        """
        # 1. 方法名
        name_node = method_node.child_by_field_name('name')
        method_name = self._get_text(name_node)

        # 2. 返回类型 (构造函数没有返回类型)
        return_type = "void"
        if not is_constructor:
            type_node = method_node.child_by_field_name('type')
            if type_node:
                return_type = self._get_text(type_node)
            else:
                # 可能是 void_type，它不是一个 field，而是直接子节点
                for child in method_node.children:
                    if child.type == 'void_type':
                        return_type = "void"
                        break

        # 3. 修饰符
        modifiers = []
        for child in method_node.children:
            if child.type == "modifiers":
                for mod in child.children:
                    # 跳过注解类型的节点，只添加真正的修饰符
                    if mod.type not in ['marker_annotation', 'annotation']:
                        modifiers.append(self._get_text(mod))

        # 4. 参数提取
        parameters = []
        params_node = method_node.child_by_field_name('parameters')
        if params_node:
            for param in params_node.children:
                if param.type == 'formal_parameter':
                    # 提取 type 和 name
                    p_type = self._get_text(param.child_by_field_name('type'))
                    p_name = self._get_text(param.child_by_field_name('name'))
                    # 某些情况下（如 int... args）结构略有不同，这里做基础处理
                    if not p_type: 
                        # 尝试直接遍历寻找类型节点
                        for child in param.children:
                            if child.type.endswith('_type'): 
                                p_type = self._get_text(child)
                                break
                    
                    parameters.append({"type": p_type, "name": p_name})

        # 5. 注释提取 (Looking backwards)
        comment = self._get_comments(method_node)

        # 6. 收集方法调用
        called_functions = self._collect_invocations(method_node)

        # 5. 提取注解
        annotations = []
        # 遍历 method_node 的所有子节点
        for child in method_node.children:
            # 如果是 modifiers 节点，检查其内部子节点
            if child.type == 'modifiers':
                for mod_child in child.children:
                    # 检查是否是注解（包括 marker_annotation 和 annotation）
                    if mod_child.type in ['marker_annotation', 'annotation']:
                        annotations.append(self._get_text(mod_child))
        
        # 获取原始方法代码
        method_code = self._get_text(method_node)
        
        # 生成代码片段字典，包含所有变体
        code_snippets = {
            "default": method_code,
        }
        
        # 方法+注释 (MD: method with docstring)
        if comment:
            code_snippets["MD"] = f"{comment}\n{method_code}"
        
        # 如果有类上下文
        if class_info:
            # 构建类声明
            class_modifiers = " ".join(class_info.get("modifiers", []))
            class_name = class_info.get("name", "")
            extends = class_info.get("extends", [])
            implements = class_info.get("implements", [])
            
            class_declaration = f"public class {class_name}"
            if class_modifiers:
                class_declaration = f"{class_modifiers} class {class_name}"
            if extends:
                class_declaration += f" extends {extends[0]}"
            if implements:
                class_declaration += f" implements {', '.join(implements)}"
            class_declaration += " {"
            
            # 方法+类上下文 (MCC: method with class context)
            method_with_context = f"{class_declaration}\n    {method_code}\n}}"
            code_snippets["MCC"] = method_with_context
            
            # 方法+注释+类上下文 (MDCC)
            if comment:
                indented_comment = "    " + comment.replace("\n", "\n    ")
                method_with_context_and_doc = f"{class_declaration}\n    {indented_comment}\n    {method_code}\n}}"
                code_snippets["MDCC"] = method_with_context_and_doc
            else:
                code_snippets["MDCC"] = method_with_context
        
        # 设置默认 enriched_code（使用原始代码作为默认值）
        final_enriched_code = method_code
        # for type,code in code_snippets.items():
        #     print(type)
        #     print(code)
        #     print()
        
        return {
            "name": method_name,
            "is_constructor": is_constructor,
            "return_type": return_type,
            "modifiers": modifiers,
            "annotations": annotations,
            "parameters": parameters,
            "called_functions": called_functions,
            "comments": comment,
            "original_code": method_code,
            "enriched_code": final_enriched_code,
            "code_snippets": code_snippets
        }

    def _get_comments(self, node):
        """
        获取节点上方的注释
        """
        comments = []
        curr = node.prev_sibling
        while curr:
            # Tree-sitter 中注释通常是 'line_comment' 或 'block_comment'
            # 注意：有时空格也会是兄弟节点，需要跳过
            if curr.type in ['line_comment', 'block_comment']:
                comments.insert(0, self._get_text(curr))
                curr = curr.prev_sibling
            elif curr.type == 'modifiers':
                # 如果遇到修饰符，说明注释在修饰符上面，继续往上找
                curr = curr.prev_sibling
            elif not curr.type.strip() or len(self._get_text(curr).strip()) == 0:
                # 跳过纯空白节点
                curr = curr.prev_sibling
            else:
                # 遇到其他代码结构，停止查找
                break
        return "\n".join(comments)

    def _collect_invocations(self, method_node):
        """
        收集方法体内的所有方法调用
        """
        invocations = set()
        
        body_node = method_node.child_by_field_name('body')
        if not body_node:
            # 可能是接口方法或抽象方法，没有 body
            return []

        # 递归查找 helper
        def traverse(node):
            if node.type == 'method_invocation':
                # 结构通常是: object.name(args) 或 name(args)
                name_node = node.child_by_field_name('name')
                if name_node:
                    func_name = self._get_text(name_node)
                    invocations.add(func_name)
            
            # 继续深度遍历所有子节点
            for child in node.children:
                traverse(child)

        traverse(body_node)
        return list(invocations)

    def analyze_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return self.analyze_code(f.read())

    def save_json(self, data, filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Result saved to: {filepath}")


def analyze_directory(directory):
    """
    分析指定目录下的所有Java文件
    分析结果保存在源代码同一目录下，文件名添加_analysis.json后缀
    如果已存在任何_analysis.json文件，则跳过整个目录
    """
    analyzer = JavaCodeAnalyzer()
    
    print(f"正在分析目录: {directory}")
    print("=" * 60)
    if not re_analyze_code :
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('_analysis.json'):
                    print(f"发现已存在的分析文件: {os.path.join(root, file)}")
                    print("目录已处理过，跳过分析")
                    print("=" * 60)
                    return
    
    analyzed_count = 0
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.java'):
                file_path = os.path.join(root, file)
                print(f"分析文件: {file_path}")
                try:
                    result = analyzer.analyze_file(file_path)
                    output_file = file_path.replace('.java', '_analysis.json')
                    analyzer.save_json(result, output_file)
                    analyzed_count += 1
                    print()
                except Exception as e:
                    print(f"分析文件 {file_path} 时出错: {e}")
                    import traceback
                    traceback.print_exc()
                    exit(1)
    
    print("=" * 60)
    print(f"分析完成！共分析 {analyzed_count} 个文件")

# --- 测试代码 ---
if __name__ == "__main__":
    test_directory = f"data\\{CONFIG['repo']}\\origin_src"
    
    if os.path.exists(test_directory):
        analyze_directory(test_directory)
    else:
        print(f"目录 {test_directory} 不存在")

