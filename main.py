import re
from pathlib import Path
from typing import List, Tuple

# インデント
IND = "    "    # 4 spaces

# 見出し判定用正規表現オブジェクト
RE_HEADING = re.compile(r'^(#{1,6})\s+(.+)$')

# 見出しレベルの状態を保持するクラス
class HeadingState:
    def __init__(self):
        self.level_counts = {2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
    
    def register(self, level: int) -> str:
        # レベル2～6以外は無視
        if level not in self.level_counts:
            return ""

        # levelのカウンタを増やす
        self.level_counts[level] += 1

        # levelより深い階層はリセット
        for lv in range(level + 1, 7):
            self.level_counts[lv] = 0
        
        # id属性値組み立て
        nums = []
        for lv in range(2, level + 1):
            nums.append(str(self.level_counts[lv]))
        # `h3-1-2`のような文字列を返す
        return f"h{level}-" + "-".join(nums)


def detect_line_type(line: str) -> str:
    """
    段落の種別を判定

    :param line: 1行分のテキスト
    :type line: str
    :return: 段落の種別を返す
    :rtype: str
    """
    stripped = line.strip()

    if stripped == "":
        return "blank"
    
    # コードブロック開始/終了（```）
    if stripped.startswith("```"):
        return "code_fence"
    
    # 見出し（`# `, `## `, ...）
    if bool(RE_HEADING.match(stripped)):
        return "heading"

    # 単一引用
    if stripped.startswith("> "):
        return "quote"
    
    # ブロック引用の開始/終了
    #   - 独自記法
    if stripped.startswith(">>>"):
        return "blockquote_start"
    if stripped.startswith("<<<"):
        return "blockquote_end"
    
    # コラムブロック
    #   - 独自記法
    if stripped.startswith("---box"):
        return "column_start"
    if  stripped.startswith("---endbox"):
        return "column_end"
    
    # 上記のどれにも該当しない -> 通常の段落
    return "paragraph"

def convert_2_heading(line: str, state: HeadingState, in_column: bool) -> str:
    """
    行のテキストに見出しタグを付ける

    :param line: 1行分のテキスト
    :type line: str
    :param state: 見出しのナンバリングの状態
    :type state: HeadingState
    :param in_column: コラム内部かどうか
    :type in_column: bool
    :return: 見出しタグで囲ったテキスト
    :rtype: str
    """
    m = RE_HEADING.match(line.strip())
    if not m:
        return line
    # `## `の部分と見出し本体を分ける
    hashes, title = m.groups()
    level = len(hashes)
    # コラム内部ではid属性不要
    if in_column:
        return f'<h{level}>{title}</h{level}>'

    # 見出しレベル1とか7以上があったらid属性なしで返す
    if level == 1 or level > 6:
        return f'<h{level}>{title}</h{level}>'

    # id属性作成
    hid = state.register(level=level)

    return f'<h{level} id="{hid}">{title}</h{level}>'

def convert_2_start_codeblock(line: str) -> Tuple[List[str], bool]:
    """ 3連バッククォートに出会ったときの処理

    :param line: 行のテキスト
    :type line: str
    :return: 開始タグ文字列, 折り畳みフラグのタプル
    :rtype: Tuple[str, bool]
    """
    stripped = line.strip()[3:] # ```を除去
    stripped = stripped.strip()
    folding = True  # デフォルトでTrue

    # 「!」が付いたら折り畳みなし
    if stripped.startswith("!"):
        folding = False
        stripped = stripped[1:] 

    # 言語名（空のときは"vbnet"にする）
    lang = stripped if stripped else "vbnet"

    # HTML開始タグを作成
    html = []
    # preタグ
    #   - 折り畳みあり
    if folding:
        html.append("<details>")
        html.append(f"{IND}<summary>ソースコードを</summary>")
        html.append(f'{IND}<pre class="line-numbers">')
    # - 折り畳みなし
    else:
        html.append('<pre class="line-numbers">')
    # codeタグ
    html.append(f'{IND * 2}<code class="language-{lang}">')

    return html, folding

def convert_paragraphs(lines: List[str]) -> List[str]:
    """
    1行ずつ段落の種別を判定し、タグ付けして返す

    :param lines: テキストのリスト
    :type lines: List[str]
    :return: タグ付け済みテキストのリスト
    :rtype: List[str]
    """
    html = []
    state = HeadingState()
    in_codeblock = False
    in_column = False
    in_blockquote = False
    folding = False
    for raw in lines:
        # 改行を取り除く
        line = raw.rstrip("\n")
        # 行の種別を判定
        lt = detect_line_type(line)
        
        # コードブロック内である
        # 一切の加工は不要 -> そのままhtmlにappend
        if in_codeblock:
            # 閉じ3連バッククォートが来た
            #   -> 閉じタグに変換してフラグを倒す
            if lt == "code_fence":
                # 折り畳みありのとき
                if folding:
                    html.append(f"{IND * 2}</code>")
                    html.append(f"{IND}</pre>")
                    html.append("</details>")
                # 折り畳みなしのとき
                else:
                    html.append(f"{IND}</code>")
                    html.append("</pre>")
                in_codeblock = False
            else:
                html.append(line)
            continue
        
        # コードブロックでない
        if lt == "paragraph":
            html.append(f"<p>{line}</p>")
        elif lt == "blank":
            pass
        elif lt == "heading":
            html.append(convert_2_heading(line, state, in_column))
        elif lt == "quote":
            # `> `よりも後（3文字目以降）をblockquoteタグで包む
            html.append(f"<blockquote>{line[2:]}</blockquote>")
        elif lt == "code_fence":
            # コードブロックフラグを立てる
            in_codeblock = True
            tags, folding = convert_2_start_codeblock(line)
            html.extend(tags)
        elif lt == "blockquote_start":
            if not in_blockquote:
                html.append('<blockquote>')
                in_blockquote = True
            # ブロッククォートがすでに開始していたらそのまま出力
            else:
                html.append(line)
        elif lt == "blockquote_end":
            if in_blockquote:
                html.append("</blockquote>")
                in_blockquote = False
            # ブロッククォート内でなかったら無視してそのまま出力
            else:
                html.append(line)
        elif lt == "column_start":
            if not in_column:
                html.append('<div class="pg-column">')
                in_column = True
            else:
                html.append(line)
        elif lt == "column_end":
            if in_column:
                html.append('</div>')
                in_column = False
            else:
                html.append(line)

    return html

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

lines = [
    "## ち～ん（笑）", 
    "### ( ´,_ゝ｀)ﾌﾟｯ", 
    "(　´_ゝ`)ﾌｰﾝ", 
    "### ((((；ﾟДﾟ))))ｶﾞｸｶﾞｸﾌﾞﾙﾌﾞﾙ", 
    "ち～ん（笑）ち～ん（笑）", 
    "ち～ん（笑）", 
    "```py", 
    "# ここはPythonのコードです", 
    "msg = \"ち～ん（笑）\"",
    "if msg == \"ち～ん（笑）\":", 
    "   return \"( ´,_ゝ｀)ﾌﾟｯ\"",  
    "```", 
    "これはPythonのコードです。"
]

# html = convert_paragraphs(lines)
# print(html)

BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "src"
OUTPUT_DIR = BASE_DIR / "dest"

if __name__ == "__main__":
    batch_convert(INPUT_DIR, OUTPUT_DIR)