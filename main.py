from pathlib import Path

from md_extentions.common import IND
from md_extentions.block_parser import convert_paragraphs

def conv_md_2_html(src: Path, dest: Path):
    # ソースファイルのテキスト行読み込み
    lines = src.read_text(encoding='utf-8').splitlines()
    # convert_paragraphs()でパース
    html_lines = convert_paragraphs(lines)

    # HTMLファイルとして書き出し
    dest.write_text("\n".join(html_lines), encoding="utf-8")
    print(f"[OK] {src.name} -> {dest}")

def batch_convert(input_dir: Path, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)

    for md_file in input_dir.glob("*.md"):
        out_file = output_dir / (md_file.stem + ".html")
        conv_md_2_html(md_file, out_file)

BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "src"
OUTPUT_DIR = BASE_DIR / "dest"

if __name__ == "__main__":
    batch_convert(INPUT_DIR, OUTPUT_DIR)