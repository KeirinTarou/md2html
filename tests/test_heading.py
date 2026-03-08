import pytest

from md_extensions.components.heading import (
    HeadingState, convert_2_heading
)

def run_headings(lines, in_column):
    state = HeadingState()
    return [convert_2_heading(line, state, in_column) for line in lines]

@pytest.mark.parametrize(
    "line, expected, in_column", [
        ("## A", '<h2 id="h2-1">A</h2>', False),  
        ("## Title", "<h2>Title</h2>", True), 
    ]
)
def test_heading(line, expected, in_column):
    assert run_headings([line], in_column)[0] == expected

@pytest.mark.parametrize(
    "lines, expected, in_column", 
    [
        (
            ["## A", "### B", "### C"], 
            [
                '<h2 id="h2-1">A</h2>', 
                '<h3 id="h3-1-1">B</h3>', 
                '<h3 id="h3-1-2">C</h3>', 
            ], 
            False
        ), 
        (
            ["## A", "### B", "## C"], 
            [
                '<h2 id="h2-1">A</h2>', 
                '<h3 id="h3-1-1">B</h3>', 
                '<h2 id="h2-2">C</h2>', 
            ], 
            False
        ), 
        (
            ["## A", "### B", "#### C"], 
            [
                '<h2 id="h2-1">A</h2>', 
                '<h3 id="h3-1-1">B</h3>', 
                '<h4 id="h4-1-1-1">C</h4>', 
            ],
            False
        ), 
        (
            ["## A", "### B", "## C"], 
            [
                "<h2>A</h2>", 
                "<h3>B</h3>", 
                "<h2>C</h2>", 
            ], 
            True
        ), 
    ]
)
def test_headings(lines, expected, in_column):
    assert run_headings(lines, in_column) == expected