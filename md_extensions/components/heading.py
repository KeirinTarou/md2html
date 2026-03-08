import re

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
    
def convert_2_heading(line: str, state: HeadingState, in_column: bool) -> str:
    """
    行のテキストに見出しタグを付ける
    - /md_extentions/block_components/heading.py

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
    
    # {}でid属性が指定されていたらそれを使う
    if title.strip().endswith("}") and "{" in title:
        text, id_part = title.rsplit("{", 1)
        custom_id = id_part[:-1]
        text = text.strip()
        return f'<h{level} id="{custom_id}">{text}</h{level}>'

    # 見出しレベル1とか7以上があったらid属性なしで返す
    if level == 1 or level > 6:
        return f'<h{level}>{title}</h{level}>'

    # id属性作成
    hid = state.register(level=level)

    return f'<h{level} id="{hid}">{title}</h{level}>'