import re
from typing import List, Tuple

from md_extensions.spec.common import IND
from md_extensions.components.heading import (
    HeadingState, convert_2_heading, RE_HEADING
)
from md_extensions.parsers.table_parser import convert_table_block
from md_extensions.parsers.inline_parser import convert_inline

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
    
    # 独自記法を先に判定する
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
    
    # テーブルブロック
    #   - 独自記法
    if stripped.startswith("---tbl-from"):
        return "table_start"
    if stripped.startswith("---tbl-to"):
        return "table_end"
    
    # コードブロック開始/終了（```）
    if stripped.startswith("```"):
        return "code_fence"
    
    # 見出し（`# `, `## `, ...）
    if bool(RE_HEADING.match(stripped)):
        return "heading"

    # 単一引用
    if stripped.startswith("> "):
        return "quote"
    
    # 箇条書き
    if stripped.startswith("- "):
        return "bullet_list"

    # 番号箇条書き
    if re.match(r"\d+\.\s+", stripped):
        return "number_list"
    
    # 上記のどれにも該当しない -> 通常の段落
    return "paragraph"

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
        html.append("<summary>ソースコードを</summary>")
        html.append('<pre class="line-numbers">')
    # - 折り畳みなし
    else:
        html.append('<pre class="line-numbers">')
    # codeタグ
    html.append(f'<code class="language-{lang}">')

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
    in_blockquote = False
    in_column = False
    in_table = False
    in_bullet_list = False
    in_number_list = False
    # コードブロック先頭行を保持しておく変数
    code_fence_open_line = None
    # コードブロック用の行をため込むリストを用意
    codeblock_buffer = []
    # テーブル要素用の行をため込むリストを用意
    table_buffer = []
    # 箇条書きの`li`をため込むリストを用意
    bullet_list_buffer = []
    number_list_buffer = []
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
                # 開始3連バッククォートを開始タグに変換
                tags, folding = convert_2_start_codeblock(code_fence_open_line)
                html.extend(tags)
                # ため込んでいたコードブロックの内容を展開
                # コードブロックの1行目は`<code>`の直後に追記
                html[-1] += codeblock_buffer[0]
                # 2行目以降はふつうにリスト`html`に追加
                for item in codeblock_buffer[1:-1]:
                    html.append(item)
                # 最後の行は`</code>`の直前にくっつける
                # 複数行のとき
                if len(codeblock_buffer) > 1:
                    html.append(codeblock_buffer[-1] + "</code>")
                # コードブロック内が1行だけのとき
                else:
                    html[-1] += "</code>"
                # 閉じタグ
                html.append("</pre>")
                # 折りたたみありの場合
                if folding:
                    html.append("</details>")

                # 状態リセット
                codeblock_buffer.clear()
                in_codeblock = False
            else:
                codeblock_buffer.append(line)
            continue
        
        # コードブロックでない
        #   -> インライン書式を先に適用しておく
        line = convert_inline(line)

        # 箇条書きが終了していたら、箇条書きを畳んでから次へ
        if in_bullet_list and (lt != "bullet_list"):
            for item in bullet_list_buffer:
                html.append(f"{IND}<li>{item}</li>")
            html.append("</ul>")
            in_bullet_list = False
            bullet_list_buffer.clear()
        if in_number_list and (lt != "number_list"):
            for item in number_list_buffer:
                html.append(f"{IND}<li>{item}</li>")
            html.append("</ol>")
            in_number_list = False
            number_list_buffer.clear()

        # 通常の段落
        if not in_table and lt == "paragraph":
            html.append(f"<p>{line}</p>")
        # 空白
        elif lt == "blank":
            pass
        # 見出し
        elif lt == "heading":
            html.append(convert_2_heading(line, state, in_column))
        # コードブロック開始（```）
        elif lt == "code_fence":
            # この行を覚えておく
            code_fence_open_line = line
            # コードブロックフラグを立てる
            in_codeblock = True
        # ブロック引用開始（>>>）
        elif lt == "blockquote_start":
            if not in_blockquote:
                html.append('<blockquote>')
                in_blockquote = True
            # ブロッククォートがすでに開始していたらそのまま出力
            else:
                html.append(line)
        # ブロック引用終了（<<<）: オリジナル
        elif lt == "blockquote_end":
            if in_blockquote:
                html.append("</blockquote>")
                in_blockquote = False
            # ブロッククォート内でなかったら無視してそのまま出力
            else:
                html.append(line)
        # コラム部開始（---box）: オリジナル
        elif lt == "column_start":
            if not in_column:
                html.append('<div class="pg-column">')
                in_column = True
            else:
                html.append(line)
        # コラム部終了（---endbox）: オリジナル
        elif lt == "column_end":
            if in_column:
                html.append('</div>')
                in_column = False
            else:
                html.append(line)
        # テーブル開始（---tbl-from）: オリジナル
        elif lt == "table_start":
            in_table = True
        # テーブル終了（---tbl-to）: オリジナル
        elif lt == "table_end":
            in_table = False
            # ため込んだテーブル要素用のリストを変換 -> 展開して追加
            html.extend(convert_table_block(table_buffer))
            # ここでため込んだテーブル要素用のリストをクリア
            table_buffer.clear()
        # 1行引用
        elif lt == "quote":
            # `> `よりも後（3文字目以降）をblockquoteタグで包む
            html.append(f"<blockquote>{line[2:]}</blockquote>")
        # 箇条書き
        elif lt == "bullet_list":
            # まだ`in_list`フラグが立っていないとき
            #   -> リスト行開始
            if not in_bullet_list:
                in_bullet_list = True
                html.append("<ul>")
            # li要素をため込んでいく
            # bullet-listの場合は3文字目以降固定で良い
            bullet_list_buffer.append(f"{line[2:]}")
        # 番号箇条書き
        elif lt == "number_list":
            if not in_number_list:
                in_number_list = True
                html.append("<ol>")
            pos = line.find(" ")
            number_list_buffer.append(f"{line[pos + 1:]}")
        # その他（テーブル内など）
        else:
            # テーブル行をスキャン中は各行をtable_bufferに追加
            if in_table:
                table_buffer.append(line)

    # この時点で箇条書きがフラグが立っているとき
    #   -> ul or olを作って追加
    if in_bullet_list: 
        for item in bullet_list_buffer:
            html.append(f"{IND}<li>{item}</li>")
        html.append("</ul>")
    if in_number_list: 
        for item in number_list_buffer:
            html.append(f"{IND}<li>{item}</li>")
        html.append("</ol>")
    
    return html