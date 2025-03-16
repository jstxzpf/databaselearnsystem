"""
Markdown预览器 - 在单独进程中预览Markdown内容
"""

import sys
import os
import webview
import argparse

def preview_markdown(filepath, title="Markdown内容预览"):
    """预览Markdown文件
    
    Args:
        filepath: HTML文件路径
        title: 窗口标题
    """
    # 确保文件存在
    if not os.path.exists(filepath):
        print(f"错误: 文件 {filepath} 不存在!")
        return
    
    # 创建URL
    file_url = f"file://{os.path.abspath(filepath)}"
    
    # 创建窗口并显示
    try:
        print(f"正在打开预览窗口: {filepath}")
        window = webview.create_window(title, file_url, width=900, height=700)
        webview.start()
    except Exception as e:
        print(f"创建窗口失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Markdown预览器")
    parser.add_argument("filepath", help="要预览的HTML文件路径")
    parser.add_argument("--title", help="窗口标题", default="Markdown内容预览")
    
    args = parser.parse_args()
    preview_markdown(args.filepath, args.title) 