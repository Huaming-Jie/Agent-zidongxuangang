import subprocess
import sys
import os
import webbrowser
import time

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(base_dir, 'backend')
    frontend_file = os.path.join(base_dir, '自动化简历优化与岗位匹配 Agen.html')

    print("=" * 50)
    print("智能简历优化与岗位匹配系统")
    print("=" * 50)
    print()

    # Check if backend is already running
    print("检查后端服务状态...")
    # We'll just start it; uvicorn will handle port conflicts

    # Start backend server
    print("启动后端 API 服务 (http://localhost:8000)...")
    backend_process = subprocess.Popen(
        [sys.executable, 'start.py'],
        cwd=backend_dir,
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )

    # Wait a bit for backend to start
    time.sleep(3)

    # Start frontend HTTP server
    print("启动前端 HTTP 服务 (http://localhost:8080)...")
    frontend_process = subprocess.Popen(
        [sys.executable, '-m', 'http.server', '8080'],
        cwd=base_dir,
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )

    # Wait for frontend server to start
    time.sleep(2)

    # Open browser
    frontend_url = 'http://localhost:8080/自动化简历优化与岗位匹配%20Agen.html'
    print(f"正在打开浏览器: {frontend_url}")
    webbrowser.open(frontend_url)

    print()
    print("=" * 50)
    print("服务已启动！")
    print("- 后端 API: http://localhost:8000")
    print("- 前端页面: http://localhost:8080")
    print("=" * 50)
    print()
    print("按 Ctrl+C 停止服务...")

    try:
        backend_process.wait()
    except KeyboardInterrupt:
        print("\n正在停止服务...")
        backend_process.terminate()
        frontend_process.terminate()
        print("服务已停止")

if __name__ == '__main__':
    main()
