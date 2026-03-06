import re

from md_extentions.format_map import FORMAT_CLASS_MAP

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
RE_CODE = re.compile(r'`([^`]+)`')

def convert_inline(text: str) -> str:

    codes = []

    def code_repl(m):
        codes.append(m.group(1))
        return f"\uE000{len(codes) - 1}\uE000"
    
    text = RE_CODE.sub(code_repl, text)

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
    
    text = RE_INLINE.sub(repl, text)

    # 退避していたインラインコード文字列を復元
    for i, c in enumerate(codes):
        text = text.replace(f"\uE000{i}\uE000", f"<code>{c}</code>")
    # 変換後の文字列を返却
    return text
    