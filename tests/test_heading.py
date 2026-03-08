import pytest

from md_extensions.components.heading import (
    HeadingState, convert_2_heading
)

def run_headings(lines, in_column):
    state = HeadingState()
    return [convert_2_heading(line, state, in_column) for line in lines]

@pytest.mark.parametrize(
    "line, expected, in_column", [
        pytest.param(
            "## A", '<h2 id="h2-1">A</h2>', False, 
            id="not_in_column"
        ),   
        pytest.param(
            "## Title", "<h2>Title</h2>", True, 
            id="in_column"
        ), 
    ]
)
def test_heading(line, expected, in_column):
    assert run_headings([line], in_column)[0] == expected

@pytest.mark.parametrize(
    "lines, expected, in_column", 
    [
        pytest.param(
            ["## A", "### B", "### C"], 
            [
                '<h2 id="h2-1">A</h2>', 
                '<h3 id="h3-1-1">B</h3>', 
                '<h3 id="h3-1-2">C</h3>', 
            ], 
            False, 
            id="normal_hierarchy",  
        ), 
        pytest.param(
            ["## A", "### B", "## C"], 
            [
                '<h2 id="h2-1">A</h2>', 
                '<h3 id="h3-1-1">B</h3>', 
                '<h2 id="h2-2">C</h2>', 
            ], 
            False, 
            id="reset_to_h2"
        ), 
        pytest.param(
            ["## A", "### B", "#### C"], 
            [
                '<h2 id="h2-1">A</h2>', 
                '<h3 id="h3-1-1">B</h3>', 
                '<h4 id="h4-1-1-1">C</h4>', 
            ],
            False, 
            id="descending_h2_to_h4"
        ), 
        pytest.param(
            ["## A", "### B", "## C"], 
            [
                "<h2>A</h2>", 
                "<h3>B</h3>", 
                "<h2>C</h2>", 
            ], 
            True, 
            id="headers_in_column"
        ), 
        pytest.param(
            ["## A", "##### B{list-1}", "## C"], 
            [
                '<h2 id="h2-1">A</h2>', 
                '<h5 id="list-1">B</h5>', 
                '<h2 id="h2-2">C</h2>', 
            ], 
            False, 
            id="override_id_attr"
        ), 
    ]
)
def test_headings(lines, expected, in_column):
    assert run_headings(lines, in_column) == expected