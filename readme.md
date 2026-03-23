## 使い方 How to use
- `md2html`プロジェクトフォルダ内の`parser`フォルダをカレントディレクトリにする。
- `parser/src`フォルダ直下に`.md`ファイルを置く。
- 次のコマンドでスクリプトを実行する。
```bash
python main.py
```
- `src`フォルダ直下の`.md`ファイルを`.html`に変換する。
- 変換後の`.html`ファイルは`parser/dest`フォルダ内に生える。
- `parser/dest`フォルダにある`template.html`に内容を貼り付けると、ざっくりとした表示イメージをブラウザで確認できる。
- Gitのリポジトリは`parser`フォルダ。

### 基本仕様
- 基本的には通常のMarkdownを踏襲
    - `_text_`: `<em></em>`
    - `__text__`: `<strong></strong>`
    - バッククォートで括る: `<code>code</code>`
    - `# `, `## `, ...: 見出し
    - `> `: 単行引用
    - `- `: bullet list
    - `1. `, `2. `, ...: number list
        - ただし、Markdown側の使用番号にかかわらず1., 2., 3., ...になる
    - 特殊文字は`\`でエスケープ可能

### 独自仕様
- 見出しのid属性
    - 基本的にレベル2以下の見出しについては階層状に振られる
        - `h2-1` -> `h3-1-1` -> `h4-1-1-1` -> ...
    - `##### リスト1{list-1}`のように書くことでid属性をオーバーライド可
        - -> `<h5 id="list-1">リスト1</h5>`

- ブロック引用
    - `>>>`と`<<<`で囲む
```bash
>>>
paragraph
paragraph
...
<<<
```

- コラム
    - `---box`と`---endbox`で囲む
    - コラム内では見出しにid属性は付与しない
```bash
---box
paragraph
paragraph
...
---endbox
```

- テーブル
    - `---tbl-from`と`---tbl-to`で囲む
    - 表自体の書き方は通常のMarkdownと同じ
```bash
---tbl-from
| default align | align-left | align-center | align-right |
| --- | :--- | :---: | ---: |
| default | left | center | right |
---tbl-to
```

- インライン書式
    - `@@{key1 key2 key3 ...}text@@`の形で書式を指定する
    - 書式指定文字列は次のとおり
```py
FORMAT_CLASS_MAP = {
    "xl": "f-sz-xl", 
    "lg": "f-sz-lg", 
    "sm": "f-sz-sm", 
    "xs": "f-sz-xs", 

    "white": "fc-white", 
    "silver": "fc-silver", 
    "red": "fc-red", 
    "tomato": "fc-tomato", 
    "orange": "fc-orange", 
    "gold": "fc-gold", 
    "deeppink": "fc-deeppink", 
    "yellow": "fc-yellow", 
    "lime": "fc-lime", 
    "cyan": "fc-cyan", 
    "skyblue": "fc-skyblue", 
    
    "strike": "fst-strike", 
    "bold": "fst-bold", 
    "italic": "fst-italic", 

    "bg-black": "bg-black", 
    "bg-white": "bg-white", 
    "bg-darkgray": "bg-darkgray", 
    "bg-red": "bg-red", 
    "bg-tomato": "bg-tomato", 
    "bg-gold": "bg-gold", 
    "bg-blue": "bg-blue", 
    "bg-yellow": "bg-yellow", 
    "bg-orange": "bg-orange", 
    "bg-pastelpink": "bg-pastelpink", 
    "bg-pastelorange": "bg-pastelorange", 
    "bg-pastelyellow": "bg-pastelyellow", 
    "bg-pastellemon": "bg-pastellemon", 
    "bg-pastelgreen": "bg-pastelgreen", 
    "bg-pastelblue": "bg-pastelblue", 
    "bg-pastelpurple": "bg-pastelpurple", 
}
```