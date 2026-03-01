from typing import List
from md_extentions.common import IND

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
    for line in lines:
        line = line.strip()
        # 空行は無視
        if not line:
            continue
        # Markdown風のセル分割
        if not line.startswith("|") or not line.endswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]

        # ヘッダ行のパース
        if not header_done:
            html.append(f'{IND}<thead>')
            html.append(f'{IND * 2}<tr>' + ''.join(f'<th>{c}</th>' for c in cells) + '</tr>')
            html.append(f'{IND}</thead>')
            html.append(f'{IND}<tbody>')
            header_done = True
            continue

        # 区切り行 -> アラインメント情報取り出し -> 要素としては無視
        if all(c.replace("-", "").replace(":", "") == "" for c in cells):
        
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
            align = alignments[i] if alignments else "left"
            row_html.append(f'<td class="align-{align}">{c}</td>')
        html.append(f'{IND * 2}<tr>' + ''.join(row_html) + '</tr>')
    
    html.append(f'{IND * 2}</tbody>')
    html.append('</table>')
    # table要素内の各行を詰め込んだリストを返却
    return html