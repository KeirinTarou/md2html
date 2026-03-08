import pytest

from md_extensions.parsers.inline_parser import convert_inline

@pytest.mark.parametrize(
    "src, expected", 
    [
        ("This is *italic*.", "This is <em>italic</em>."), 
        ("This is _italic_.", "This is <em>italic</em>."), 
        (r"This is not \*italic\*.", "This is not *italic*."), 
        (r"This is not \_italic\_.", "This is not _italic_."), 
        (r"*italic \* inside*", "<em>italic * inside</em>"), 
        (r"**bold *italic* bold**", "<strong>bold <em>italic</em> bold</strong>"), 
        (r"**bold _italic_ bold**", "<strong>bold <em>italic</em> bold</strong>"), 
        (r"Shift\_JIS is a Shift\_JIS.", "Shift_JIS is a Shift_JIS."), 
        (r"\* \_ \` \[ \] \( \)", "* _ ` [ ] ( )"), 
    ]
)
def test_inline(src, expected):
    assert convert_inline(src) == expected