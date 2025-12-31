import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    # 优先查找外部资源（允许用户自定义）
    if getattr(sys, 'frozen', False):
        # 打包后，优先看 EXE 旁边有没有
        application_path = os.path.dirname(sys.executable)
        external_path = os.path.join(application_path, relative_path)
        if os.path.exists(external_path):
            return external_path
        
    # 如果外部没有，或者是开发环境，使用默认逻辑
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)
