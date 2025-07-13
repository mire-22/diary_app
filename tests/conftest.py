import os
import pytest
import importlib.util
import importlib.machinery

# srcディレクトリの絶対パス
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))

@pytest.fixture(autouse=True, scope='session')
def add_src_to_path():
    """
    srcディレクトリをimportパスに追加（sys.pathは使わずimportlibで）
    """
    if SRC_DIR not in os.environ.get('PYTHONPATH', ''):
        os.environ['PYTHONPATH'] = SRC_DIR + os.pathsep + os.environ.get('PYTHONPATH', '') 