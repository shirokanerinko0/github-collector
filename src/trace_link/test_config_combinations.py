#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试不同配置组合的脚本
测试 config.json 中 code_snippet 配置的不同组合
"""

import os
import json
import subprocess
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
CONFIG_FILE = os.path.join(PROJECT_ROOT, 'config.json')
MAIN_SCRIPT = os.path.join(PROJECT_ROOT, 'src', 'trace_link', 'main.py')

def save_original_config():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def restore_original_config(original_config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(original_config, f, indent=2, ensure_ascii=False)

def update_config(code_snippet):
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)

    config['code_snippet'] = code_snippet

    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def run_test(code_snippet):
    print(f"\n" + "=" * 80)
    print(f"测试配置: code_snippet={code_snippet}")
    print("=" * 80)

    update_config(code_snippet)

    print("\n开始运行 main.py...")
    result = subprocess.run(
        [sys.executable, MAIN_SCRIPT],
        cwd=PROJECT_ROOT,
        capture_output=False,
        text=True,
        encoding='utf-8'
    )

    print(f"\n返回码: {result.returncode}")

def main():
    original_config = save_original_config()

    fixed_base_snippets = ["IO", "IMO", "IMD"]

    try:
        combinations = [
            ["CO","MO"],
            ["CO","MCC"],
            ["CO","MD"],
            ["CO","MDCC"],
            ["CO","MO","MC"],
            ["CO","MCC","MC"],
            ["CO","MD","MC"],
            ["CO","MDCC","MC"],
            ["CO","MCC","MO"],
            ["CO","MD","MO"],
            ["CO","MDCC","MO"],
            ["CO","MO","MC"],
            ["CO","MCC","MC","MO"],
            ["CO","MD","MC","MO"],
            ["CO","MDCC","MC","MO"],
        ]

        all_tests = []
        for combo in combinations:
            combined = list(set(combo + fixed_base_snippets))
            all_tests.append(combined)

        print(f"总共需要测试 {len(all_tests)} 个配置组合\n")

        for i, code_snippet in enumerate(all_tests, 1):
            print(f"\n开始测试组合 {i}/{len(all_tests)}: {code_snippet}")
            run_test(code_snippet)

        print("\n" + "=" * 80)
        print("测试结果总结")
        print("=" * 80)

    finally:
        restore_original_config(original_config)
        print("\n已恢复原始配置")

if __name__ == "__main__":
    main()