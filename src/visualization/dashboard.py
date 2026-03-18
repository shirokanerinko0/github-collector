import os
import sys
import json
import time
import subprocess
import threading
import html
from datetime import datetime
from queue import Queue, Empty

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.utils.utils import load_config, save_config
from src.model.calculate_code_vectors import get_pt_file_name
st.set_page_config(
    page_title="需求追踪链接工具",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)
pt_file_name = get_pt_file_name()
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #666;
    }
    .stButton>button {
        width: 100%;
    }
    .success-msg {
        background-color: #d4edda;
        color: #155724;
        padding: 0.5rem;
        border-radius: 5px;
    }
    .error-msg {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.5rem;
        border-radius: 5px;
    }
    .log-output {
        background-color: #1e1e1e;
        color: #d4d4d4;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 12px;
        padding: 10px;
        border-radius: 5px;
        max-height: 300px;
        overflow-y: auto;
        overflow-x: auto;
        white-space: pre;
    }
    .log-output pre {
        margin: 0;
        white-space: pre;
    }
</style>
""", unsafe_allow_html=True)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
CONFIG_FILE = "config.json"
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

def get_available_repos():
    if not os.path.exists(DATA_DIR):
        return []
    repos = []
    for item in os.listdir(DATA_DIR):
        item_path = os.path.join(DATA_DIR, item)
        if os.path.isdir(item_path) and not item.startswith('.'):
            repos.append(item)
    return sorted(repos)

def get_trace_link_files(repo):
    repo_path = os.path.join(DATA_DIR, repo)
    if not os.path.exists(repo_path):
        return []
    files = []
    for f in os.listdir(repo_path):
        if f.startswith('trace_link') and f.endswith('.json'):
            files.append(f)
    return sorted(files, reverse=True)

def load_trace_link_data(repo, filename):
    filepath = os.path.join(DATA_DIR, repo, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def run_command(command, cwd=None):
    if cwd is None:
        cwd = PROJECT_ROOT
    
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUTF8'] = '1'
    
    result = subprocess.run(
        command,
        shell=True,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        env=env
    )
    return result

def run_command_realtime(command, output_placeholder, cwd=None, prefix=""):
    if cwd is None:
        cwd = PROJECT_ROOT
    
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUTF8'] = '1'
    
    process = subprocess.Popen(
        command,
        shell=True,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8',
        errors='replace',
        bufsize=1,
        env=env
    )
    
    output_lines = []
    scroll_id = f"scroll-{id(output_placeholder)}"
    for line in iter(process.stdout.readline, ''):
        output_lines.append(line)
        current_output = prefix + ''.join(output_lines)
        escaped_output = html.escape(current_output)
        output_placeholder.markdown(f'''
            <div class="log-output" id="{scroll_id}"><pre>{escaped_output}</pre></div>
            <script>
                var element = document.getElementById("{scroll_id}");
                if (element) {{ element.scrollTop = element.scrollHeight; }}
            </script>
            ''', unsafe_allow_html=True)
    
    process.stdout.close()
    return_code = process.wait()
    
    return prefix + ''.join(output_lines), return_code

def main():
    st.markdown('<div class="main-header">TRae - 需求追踪链接工具</div>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("配置面板")
        
        config = load_config()
        
        st.subheader("仓库设置")
        owner = st.text_input("Owner", value=config.get('owner', 'google'))
        repo = st.text_input("Repository", value=config.get('repo', 'guava'))
        token = st.text_input("GitHub Token", value=config.get('token', ''), type="password")
        
        st.subheader("采集限制")
        limits = config.get('limits', {})
        max_issues = st.number_input("最大Issues数", min_value=1, max_value=1000, value=limits.get('max_issues', 100), help="限制采集的Issues数量")
        max_pull_requests = st.number_input("最大PR数", min_value=1, max_value=1000, value=limits.get('max_pull_requests', 100), help="限制采集的Pull Requests数量")
        
        st.subheader("过滤设置")
        filter_labels_str = st.text_input(
            "过滤标签", 
            value=','.join(config.get('filter_labels', [])),
            help="筛选特定标签的Issues，多个标签用逗号分隔，如: type=addition,type=bug"
        )
        filter_labels = [label.strip() for label in filter_labels_str.split(',') if label.strip()]
        
        issue_state = st.selectbox(
            "Issue状态",
            options=['open', 'closed', 'all'],
            index=['open', 'closed', 'all'].index(config.get('issue_state', 'closed')),
            help="筛选指定状态的Issues"
        )
        
        st.subheader("模型设置")
        encode_model = st.selectbox(
            "编码模型",
            options=['unixcoder', 'jina_code', 'jina_v2'],
            index=['unixcoder', 'jina_code', 'jina_v2'].index(config.get('encode_model_name', 'unixcoder'))
        )
        top_k = st.slider("Top-K", min_value=1, max_value=20, value=config.get('top_k', 5))
        
        st.subheader("高级设置")
        use_llm_processing = st.checkbox("使用LLM处理需求", value=config.get('requirement_processing', {}).get('use_llm_processing', False))
        use_llm_trace = st.checkbox("使用LLM验证链接", value=config.get('trace_link', {}).get('use_llm', False))
        
        analyze_by_method = st.checkbox("按方法分析", value=config.get('analyze_by_method', True))
        analyze_full_code = st.checkbox("分析完整代码", value=config.get('analyze_full_code', False))
        
        if st.button("保存配置", use_container_width=True):
            new_config = config.copy()
            new_config['owner'] = owner
            new_config['repo'] = repo
            new_config['token'] = token
            new_config['limits'] = {
                'max_issues': max_issues,
                'max_pull_requests': max_pull_requests
            }
            new_config['filter_labels'] = filter_labels
            new_config['issue_state'] = issue_state
            new_config['encode_model_name'] = encode_model
            new_config['top_k'] = top_k
            new_config['requirement_processing']['use_llm_processing'] = use_llm_processing
            new_config['trace_link']['use_llm'] = use_llm_trace
            new_config['analyze_by_method'] = analyze_by_method
            new_config['analyze_full_code'] = analyze_full_code
            save_config(new_config)
            st.success("配置已保存!")
    
    tab1, tab2, tab3, tab4 = st.tabs(["主页", "结果分析", "详细数据", "对比分析"])
    
    with tab1:
        st.header("操作面板")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("数据采集")
            
            if st.button("采集GitHub数据", use_container_width=True, key="btn_collect"):
                output_placeholder = st.empty()
                output, return_code = run_command_realtime("python -u main.py", output_placeholder)
                if return_code == 0:
                    st.success("数据采集完成!")
                else:
                    st.error(f"执行失败，返回码: {return_code}")
            
            if st.button("下载仓库代码", use_container_width=True, key="btn_download"):
                output_placeholder = st.empty()
                output, return_code = run_command_realtime("python -u file_operations/download.py", output_placeholder)
                if return_code == 0:
                    st.success("仓库下载完成!")
                else:
                    st.error(f"执行失败，返回码: {return_code}")
        
        with col2:
            st.subheader("代码分析")
            
            if st.button("分析代码结构", use_container_width=True, key="btn_analyze"):
                output_placeholder = st.empty()
                output, return_code = run_command_realtime("python -u -c \"from src.JavaCodeAnalyzer.tree_sitter_java_analyzer import analyze_directory; analyze_directory('data/' + __import__('json').load(open('config.json'))['repo'] + '/origin_src')\"", output_placeholder)
                if return_code == 0:
                    st.success("代码分析完成!")
                else:
                    st.error(f"执行失败，返回码: {return_code}")
            
            if st.button("计算代码向量", use_container_width=True, key="btn_vectors"):
                output_placeholder = st.empty()
                output, return_code = run_command_realtime("python -u src/model/calculate_code_vectors.py", output_placeholder)
                if return_code == 0:
                    st.success("向量计算完成!")
                else:
                    st.error(f"执行失败，返回码: {return_code}")
        
        with col3:
            st.subheader("追踪链接")
            
            if st.button("生成追踪链接", use_container_width=True, key="btn_trace"):
                output_placeholder = st.empty()
                output, return_code = run_command_realtime("python -u src/trace_link/main.py", output_placeholder)
                if return_code == 0:
                    st.success("追踪链接生成完成!")
                else:
                    st.error(f"执行失败，返回码: {return_code}")
            
            if st.button("运行完整流程", use_container_width=True, type="primary", key="btn_full"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                output_area = st.empty()
                
                steps = [
                    ("采集GitHub数据", "python -u main.py"),
                    ("下载仓库代码", "python -u file_operations/download.py"),
                    ("计算代码向量", "python -u src/model/calculate_code_vectors.py"),
                    ("生成追踪链接", "python -u src/trace_link/main.py")
                ]
                
                full_output = ""
                for i, (step_name, cmd) in enumerate(steps):
                    status_text.text(f"正在执行: {step_name}...")
                    full_output += f"\n{'='*50}\n[{step_name}]\n{'='*50}\n"
                    
                    output, return_code = run_command_realtime(cmd, output_area, prefix=full_output)
                    full_output = output
                    
                    if return_code != 0:
                        st.error(f"{step_name} 失败，返回码: {return_code}")
                        break
                    
                    progress_bar.progress((i + 1) / len(steps))
                else:
                    status_text.text("所有步骤完成!")
                    st.success("完整流程执行完成!")
        
        st.divider()
        
        st.header("数据文件")
        available_repos = get_available_repos()
        if available_repos:
            selected_repo = st.selectbox("选择仓库", available_repos, index=0, key="repo_main")
            repo_path = os.path.join(DATA_DIR, selected_repo)
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("数据文件")
                data_files = {
                    'requirements_raw.json': '原始需求数据',
                    'requirements_processed.json': '预处理需求',
                    'requirements_processed_llm.json': 'LLM处理需求',
                    pt_file_name: '代码向量文件'
                }
                for fname, desc in data_files.items():
                    fpath = os.path.join(repo_path, fname)
                    exists = "✅" if os.path.exists(fpath) else "❌"
                    st.text(f"{exists} {desc}")
            
            with col2:
                st.subheader("追踪链接结果")
                trace_files = get_trace_link_files(selected_repo)
                if trace_files:
                    for tf in trace_files[:5]:
                        st.text(f"{tf}")
                else:
                    st.info("暂无追踪链接结果")
        else:
            st.info("请先运行数据采集，或检查 data 目录")
    
    with tab2:
        st.header("结果分析")
        
        available_repos = get_available_repos()
        if not available_repos:
            st.info("请先运行数据采集")
        else:
            col1, col2 = st.columns([1, 2])
            with col1:
                selected_repo = st.selectbox("选择仓库", available_repos, key="repo_analyze")
                trace_files = get_trace_link_files(selected_repo)
                if trace_files:
                    selected_file = st.selectbox("选择结果文件", trace_files)
                else:
                    st.warning("该仓库暂无追踪链接结果")
                    selected_file = None
            
            with col2:
                if trace_files and selected_file:
                    data = load_trace_link_data(selected_repo, selected_file)
                    if data:
                        stats = data.get('statistics', {})
                        
                        col_a, col_b, col_c, col_d = st.columns(4)
                        with col_a:
                            st.metric("总需求数", stats.get('total_requirements', 0))
                        with col_b:
                            st.metric("有变更文件", stats.get('requirements_with_change_files', 0))
                        with col_c:
                            st.metric("至少命中一个", stats.get('requirements_with_at_least_one_hit', 0))
                        with col_d:
                            recall = stats.get('overall_recall', 0)
                            st.metric("整体召回率", f"{recall:.2%}")
                        
                        col_e, col_f, col_g = st.columns(3)
                        with col_e:
                            st.metric("总变更文件", stats.get('total_change_files', 0))
                        with col_f:
                            st.metric("命中文件数", stats.get('total_hit_files', 0))
                        with col_g:
                            st.metric("Top-K", stats.get('top_k', 5))
                        
                        st.divider()
                        
                        results = data.get('results', [])
                        recalls = []
                        for r in results:
                            if 'recall' in r:
                                recalls.append({
                                    'req_id': r['req_id'],
                                    'title': r['req_title'][:30] + '...' if len(r['req_title']) > 30 else r['req_title'],
                                    'recall': r['recall']['recall'],
                                    'hit': r['recall']['hit_count'],
                                    'total': r['recall']['total_change_files']
                                })
                        
                        if recalls:
                            df = pd.DataFrame(recalls)
                            
                            fig = make_subplots(rows=1, cols=2, 
                                               subplot_titles=('各需求召回率', '召回率分布'))
                            
                            colors = ['green' if r > 0 else 'red' for r in df['recall']]
                            fig.add_trace(
                                go.Bar(x=df['req_id'], y=df['recall'], marker_color=colors,
                                       text=[f"{r:.0%}" for r in df['recall']], textposition='outside'),
                                row=1, col=1
                            )
                            
                            fig.add_trace(
                                go.Histogram(x=df['recall'], nbinsx=10, marker_color='#1f77b4'),
                                row=1, col=2
                            )
                            
                            fig.update_layout(height=400, showlegend=False)
                            fig.update_xaxes(tickangle=45, row=1, col=1)
                            st.plotly_chart(fig, use_container_width=True)
                            
                            st.subheader("召回率详情")
                            st.dataframe(df.style.format({'recall': '{:.2%}'}), use_container_width=True)
    
    with tab3:
        st.header("详细数据")
        
        available_repos = get_available_repos()
        if not available_repos:
            st.info("请先运行数据采集")
        else:
            col1, col2 = st.columns([1, 3])
            with col1:
                selected_repo = st.selectbox("选择仓库", available_repos, key="repo_detail")
                trace_files = get_trace_link_files(selected_repo)
                if trace_files:
                    selected_file = st.selectbox("选择结果文件", trace_files, key="file_detail")
                else:
                    st.warning("该仓库暂无追踪链接结果")
                    selected_file = None
            
            with col2:
                if trace_files and selected_file:
                    data = load_trace_link_data(selected_repo, selected_file)
                    if data:
                        results = data.get('results', [])
                        
                        req_options = [f"{r['req_id']}: {r['req_title'][:40]}..." for r in results]
                        selected_idx = st.selectbox("选择需求", range(len(req_options)), 
                                                   format_func=lambda x: req_options[x])
                        
                        if selected_idx is not None:
                            req = results[selected_idx]
                            
                            col_a, col_b = st.columns([2, 1])
                            with col_a:
                                st.subheader(f"{req['req_id']}")
                                req_url = req.get('req_url', '')
                                if req_url:
                                    st.markdown(f"**标题:** [{req['req_title']}]({req_url})")
                                else:
                                    st.markdown(f"**标题:** {req['req_title']}")
                                st.markdown(f"**类型:** {req.get('req_type', 'N/A')}")
                                st.markdown(f"**摘要:** {req.get('req_cleaned_summary', 'N/A')}")
                                
                                with st.expander("查看完整描述"):
                                    st.text(req.get('req_description', '无描述'))
                            
                            with col_b:
                                if 'recall' in req:
                                    st.metric("召回率", f"{req['recall']['recall']:.2%}")
                                    st.metric("命中/总数", f"{req['recall']['hit_count']}/{req['recall']['total_change_files']}")
                                else:
                                    st.info("无变更文件数据")
                            
                            st.divider()
                            st.subheader("追踪链接 (Top-K)")
                            
                            links = req.get('links', [])
                            for i, link in enumerate(links):
                                with st.expander(f"#{i+1} {link['file_path']} (相似度: {link['similarity']:.4f})"):
                                    col_x, col_y = st.columns([1, 2])
                                    with col_x:
                                        st.markdown(f"**文件:** `{link['file_path']}`")
                                        st.markdown(f"**类:** `{link['class_name']}`")
                                        st.markdown(f"**方法:** `{link.get('method_name', 'N/A')}`")
                                        st.markdown(f"**相似度:** `{link['similarity']:.4f}`")
                                    
                                    with col_y:
                                        st.code(link.get('original_code', '无代码'), language='java')
                            
                            if req.get('change_files'):
                                st.divider()
                                st.subheader("实际变更文件")
                                for cf in req['change_files']:
                                    if isinstance(cf, dict):
                                        st.text(f"{cf.get('file_path', cf)} ({cf.get('status', 'N/A')})")
                                    else:
                                        st.text(f"{cf}")
    
    with tab4:
        st.header("模型对比分析")
        
        available_repos = get_available_repos()
        if not available_repos:
            st.info("请先运行数据采集")
        else:
            selected_repo = st.selectbox("选择仓库", available_repos, key="repo_compare")
            trace_files = get_trace_link_files(selected_repo)
            
            if len(trace_files) < 2:
                st.info("需要至少两个追踪链接结果文件进行对比")
            else:
                selected_files = st.multiselect("选择要对比的结果文件", trace_files, default=trace_files[:min(3, len(trace_files))])
                
                if len(selected_files) >= 2:
                    comparison_data = []
                    for f in selected_files:
                        data = load_trace_link_data(selected_repo, f)
                        if data:
                            stats = data.get('statistics', {})
                            comparison_data.append({
                                'file': f,
                                'model': f.split('_')[2] if len(f.split('_')) > 2 else 'unknown',
                                'recall': stats.get('overall_recall', 0),
                                'total_req': stats.get('total_requirements', 0),
                                'with_change': stats.get('requirements_with_change_files', 0),
                                'at_least_one': stats.get('requirements_with_at_least_one_hit', 0),
                                'total_files': stats.get('total_change_files', 0),
                                'hit_files': stats.get('total_hit_files', 0),
                                'top_k': stats.get('top_k', 5)
                            })
                    
                    df = pd.DataFrame(comparison_data)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        fig = px.bar(df, x='model', y='recall', 
                                    title='各模型召回率对比',
                                    text=[f"{r:.2%}" for r in df['recall']])
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        fig = px.bar(df, x='model', y=['at_least_one', 'with_change'],
                                    title='需求命中情况对比', barmode='group')
                        st.plotly_chart(fig, use_container_width=True)
                    
                    st.dataframe(df.style.format({'recall': '{:.2%}'}), use_container_width=True)

if __name__ == "__main__":
    main()
