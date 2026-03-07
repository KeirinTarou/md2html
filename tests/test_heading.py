from md_extensions.components.heading import (
    HeadingState, convert_2_heading
)

def test_simple_h2():
    # Arrange
    state = HeadingState()
    # Act
    html = convert_2_heading("## Title", state, False)
    # Assert
    assert html == '<h2 id="h2-1">Title</h2>'

def test_h2_counter_increment():
    # Arrange
    state = HeadingState()
    # Act
    html1 = convert_2_heading("## A", state, False)
    html2 = convert_2_heading("## B", state, False)
    # Assert
    assert html1 == '<h2 id="h2-1">A</h2>'
    assert html2 == '<h2 id="h2-2">B</h2>'

def test_nested_heading():
    # Arrange
    state = HeadingState()
    # Act
    convert_2_heading("## A", state, False)
    html = convert_2_heading("### B", state, False)
    # Assert
    assert html == '<h3 id="h3-1-1">B</h3>'

def test_heading_in_column():
    # Arrange
    state = HeadingState()
    # Act
    html = convert_2_heading("## Title", state, True)
    # Assert
    assert html == "<h2>Title<</h2>"