import sys
from pathlib import Path

"""
## テストコードの実行
- プロジェクトルートをカレントディレクトリにする
- `pytest tests\test_inline.py`コマンドを叩く
## 技術的な解説
- `conftest.py`でルートディレクトリのパスを`PYTHONPATH`に追加
    - `sys.path.append(str(Path(__file__).resolve().parents[1]))`
    - 〝このファイル〟があるディレクトリの上の上のディレクトリ
"""

sys.path.append(str(Path(__file__).resolve().parents[1]))