import re
from typing import List
from md_extensions.spec.common import IND, ESC_PIPE

RE_SEP = re.compile(r":?-{3,}:?")

def convert_table_block(lines: List[str]) -> List[str]:
    """ 独自記法`---tbl-from`～`---tbl-to`で囲まれた部分をtableタグで囲む

    :param lines: テーブル部分の行のリスト
    :type lines: List[str]
    :return: tableタグで囲んだテーブル要素の行のリスト
    :rtype: List[str]
    """
    # 開始タグが先頭の要素
    html = ['<table class="pastel-table">']
    # ヘッダ行作成済みフラグ
    header_done = False
    alignments = []
    for line in lines:
        # エスケープされた`|`を一旦退避
        line = line.replace(r"\|", ESC_PIPE)
        line = line.strip()
        # 空行は無視
        if not line:
            continue
        # Markdown風のセル分割
        if not line.startswith("|") or not line.endswith("|"):
            continue
        raw_cells = line.strip("|").split("|")
        cells = [cell.replace(ESC_PIPE, "|").strip() for cell in raw_cells]

        # ヘッダ行のパース
        if not header_done:
            html.append(f'{IND}<thead>')
            html.append(f'{IND * 2}<tr>' + ''.join(f'<th>{c}</th>' for c in cells) + '</tr>')
            html.append(f'{IND}</thead>')
            html.append(f'{IND}<tbody>')
            header_done = True
            continue

        # 区切り行 -> アラインメント情報取り出し -> 要素としては無視
        #   -> `-`か`:`しかない行 = 区切り行
        if all(RE_SEP.fullmatch(c.strip()) for c in cells):
        
            def detect_alignment(cell: str) -> str:
                cell = cell.strip()
                if cell.startswith(":-") and cell.endswith("-:"):
                    return "center"
                elif cell.startswith(":-"):
                    return "left"
                elif cell.endswith("-:"):
                    return "right"
                return "left"
            
            alignments = [detect_alignment(c) for c in cells]
            # パースはせずに次へ
            continue

        # ここまで来た -> データ行
        row_html = []
        for i, c in enumerate(cells):
            align = alignments[i] if i < len(alignments) else "left"
            row_html.append(f'<td class="align-{align}">{c}</td>')
        html.append(f'{IND * 2}<tr>' + ''.join(row_html) + '</tr>')
    
    html.append(f'{IND}</tbody>')
    html.append('</table>')
    # table要素内の各行を詰め込んだリストを返却
    return html