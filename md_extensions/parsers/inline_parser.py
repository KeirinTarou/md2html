import re

from md_extensions.spec.format_map import FORMAT_CLASS_MAP
from md_extensions.spec.common import ESCAPE_MAP

# オリジナル記法用
r"""
    `@@{xl bold red}foobar2000@@`にマッチ
        - `([^\}]*)`
            - `[^\}]`: `}`以外の任意の文字にマッチ
            - `*`: 直前の文字の0回以上の繰り返し
            - `([^\}]*)`: `}`以外の文字の0回以上の繰り返しをグループ化 
        - `(.+?)`
            - `.`: 任意の1文字
            - `+`: 直前の文字の1回以上の繰り返し
            - `?`: 
"""
RE_INLINE = re.compile(r'@@\{([^}]*)\}(.+?)@@', re.S)
# インラインコード用
RE_CODE = re.compile(r'`([^`]+)`')
# リンク用
r"""
    `[text](url){option}`にマッチ
        - `\[([^]]+)\]`: `[]`で囲まれた`]`以外の文字1文字以上にマッチ
            - `[]`の中身をキャプチャ(1) -> リンクテキスト
        - `\(([^)]+)\)`: `()`で囲まれた`)`以外の文字1文字以上にマッチ
            - `()`の中身をキャプチャ(2) -> リンクURL
        - `(?:\{([^}]+)\})?`: `{}`で囲まれた`}`以外の文字1文字以上にマッチ
            - ただし、あってもなくても良い
            - `{}`の中身をキャプチャ(3) -> オプション指定
"""
RE_LINK = re.compile(
    r'\[([^\]]+)\]\(([^)]+)\)(?:\{([^}]+)\})?'
)
# strong用
r"""
    `**text**`または`__text__`にマッチ
        - `(\*\*|__)`: `**`または`__`にマッチ -> キャプチャ(1)
        - `(.+?)`: 任意の1文字の繰り返しに非貪欲マッチ -> キャプチャ(2)
"""
RE_STRONG = re.compile(r'(\*\*|__)(.+?)\1')
# em用
r"""
    `*text*`または`_text_`にマッチ
"""
RE_EM = re.compile(r'(\*|_)(.+?)\1')

def convert_inline(text: str) -> str:
    # エスケープされた特殊文字をまとめて退避
    for src, token in ESCAPE_MAP.items():
        text = text.replace(src, token)

    codes = []

    def code_repl(match):
        idx = len(codes)
        codes.append(match.group(1))
        return f"\uE000CODE{idx}\uE000"
    
    text = RE_CODE.sub(code_repl, text)

    def link_repl(match):
        label = match.group(1)
        url = match.group(2)
        opt = match.group(3)

        attrs = f'href="{url}"'

        if opt == "blank":
            attrs += ' target="_blank" rel="noopener"'

        return f'<a {attrs}>{label}</a>'
    
    def strong_repl(match):
        return f"<strong>{match.group(2)}</strong>"
    
    def em_repl(match):
        return f"<em>{match.group(2)}</em>"

    def repl(match):
        """ 対象文字列をクラス属性付きspanで囲む
        
            - @@{xl bold red}foobar2000@@
                - -> <span class="f-sz-xl fst-bold fc-red">foobar2000</span>
        """
        fmt = match.group(1).strip()    # "xl bold red"
        content = match.group(2)        # "foobar2000"

        classes = [
            FORMAT_CLASS_MAP.get(key, key) 
            for key in fmt.split()
        ]
        
        class_attr = " ".join(classes)  # "f-sz-xl fst-bold fc-red"
        # span要素を返却
        #   -> <span class="f-sz-xl fst-bold fc-red">foobar2000</span>
        return f'<span class="{class_attr}">{content}</span>'
    
    # 独自記法のインライン書式を適用
    text = RE_INLINE.sub(repl, text)
    # リンク変換
    text = RE_LINK.sub(link_repl, text)
    # strong要素
    text = RE_STRONG.sub(strong_repl, text)
    # em要素
    text = RE_EM.sub(em_repl, text)

    # 退避していたインラインコード文字列を復元
    for i, c in enumerate(codes):
        token = f"\uE000CODE{i}\uE000"
        text = text.replace(token, f"<code>{c}</code>")

    # エスケープしていた特殊文字を復元
    for src, token in ESCAPE_MAP.items():
        text = text.replace(token, src[1])

    # 変換後の文字列を返却
    return text
    