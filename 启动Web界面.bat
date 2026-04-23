@echo off
title Clash三段式配置生成器 - Web界面
color 0A

echo.
echo  ============================================
echo.
echo    Clash三段式配置生成器 - Web可视化界面
echo.
echo  ============================================
echo.

set "PYTHON_CMD="

REM 优先尝试 py 命令（Python Launcher，最可靠）
py --version >nul 2>&1
if %errorlevel% == 0 (
    set "PYTHON_CMD=py"
    goto :python_found
)

REM 尝试 python 命令，但要排除 Windows Store 包装器
for /f "delims=" %%i in ('python --version 2^>^&1') do set "PYVER=%%i"
echo %PYVER% | findstr /I /C:"Python" >nul 2>&1
if %errorlevel% == 0 (
    python -c "import sys; print(sys.executable)" >nul 2>&1
    if %errorlevel% == 0 (
        set "PYTHON_CMD=python"
        goto :python_found
    )
)

REM 尝试 python3 命令
python3 --version >nul 2>&1
if %errorlevel% == 0 (
    set "PYTHON_CMD=python3"
    goto :python_found
)

echo  [错误] 未检测到可用的 Python 解释器
echo.
echo  原因分析：
echo  --------------------------------------------
echo   Windows 自带的 "python" 命令是 Microsoft Store 包装器，
echo   它无法直接运行 Python 脚本，必须安装完整版 Python。
echo  --------------------------------------------
echo.
echo  解决方法：
echo   1. 访问 https://www.python.org/downloads/
echo   2. 下载 Python 3.10 或更高版本（推荐 3.11/3.12）
echo   3. 安装时务必勾选 "Add Python to PATH" 和 "Install for all users"
echo   4. 安装完成后，关闭所有命令行窗口，重新双击此文件
echo.
echo  或者使用 Microsoft Store 安装：
echo   打开 Microsoft Store - 搜索 "Python" - 安装 Python 3.11
echo.
pause
exit /b 1

:python_found
for /f "delims=" %%i in ('%PYTHON_CMD% --version 2^>^&1') do echo  [检查] %%i
echo.

REM 获取端口号
set PORT=8888
if not "%~1"=="" (
    set PORT=%~1
)

echo  [配置] 服务器端口: %PORT%
echo.
echo  ============================================
echo.
echo  启动信息：
echo  --------------------------------------------
echo   访问地址: http://localhost:%PORT%
echo   工作目录: %CD%
echo   启动时间: %date% %time%
echo  --------------------------------------------
echo.
echo  提示：
echo   * 系统将自动打开浏览器
echo   * 如未自动打开，请手动访问上述地址
echo   * 按 Ctrl+C 停止服务器
echo.
echo  ============================================
echo.

REM 启动Web服务器
%PYTHON_CMD% config_generator_web.py %PORT%

REM 服务器停止后的提示
echo.
echo  ============================================
echo.
echo  服务器已停止
echo.
echo  感谢使用 Clash三段式配置生成器！
echo.
echo  ============================================
echo.
pause
