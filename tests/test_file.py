import pytest

from hide import model


def test_file_str():
    file = model.File(
        path="README.md",
        lines=[
            model.Line(number=1, content="Hello World"),
            model.Line(number=2, content="This is a test"),
            model.Line(number=3, content="Thanks bye"),
        ],
    )

    expected_output = """\
1 | Hello World
2 | This is a test
3 | Thanks bye
"""

    assert str(file) == expected_output


def test_file_str_with_diagnostics():
    file = model.File(
        path="README.md",
        lines=[
            model.Line(number=1, content="Hello World"),
            model.Line(number=2, content="This is a test"),
            model.Line(number=3, content="Thanks bye"),
        ],
        diagnostics=[
            model.Diagnostic(
                range=model.Range(
                    start=model.Position(line=0, character=0),
                    end=model.Position(line=0, character=5),
                ),
                severity=model.DiagnosticSeverity.Error,
                code="E0001",
                message="This is an error",
            ),
            model.Diagnostic(
                range=model.Range(
                    start=model.Position(line=1, character=0),
                    end=model.Position(line=1, character=4),
                ),
                severity=model.DiagnosticSeverity.Warning,
                code="W0001",
                message="This is a warning",
            ),
        ],
    )

    expected_output = """\
1 | Hello World
    ^^^^^ Error: This is an error

2 | This is a test
    ^^^^ Warning: This is a warning

3 | Thanks bye
"""

    assert str(file) == expected_output


def test_file_str_with_multiple_diagnostics_for_same_line():
    file = model.File(
        path="README.md",
        lines=[
            model.Line(number=1, content="Hello World"),
            model.Line(number=2, content="This is a test"),
            model.Line(number=3, content="Thanks bye"),
        ],
        diagnostics=[
            model.Diagnostic(
                range=model.Range(
                    start=model.Position(line=0, character=0),
                    end=model.Position(line=0, character=5),
                ),
                severity=model.DiagnosticSeverity.Error,
                code="E0001",
                message="This is an error",
            ),
            model.Diagnostic(
                range=model.Range(
                    start=model.Position(line=1, character=0),
                    end=model.Position(line=1, character=4),
                ),
                severity=model.DiagnosticSeverity.Warning,
                code="W0001",
                message="This is a warning",
            ),
            model.Diagnostic(
                range=model.Range(
                    start=model.Position(line=1, character=5),
                    end=model.Position(line=1, character=7),
                ),
                severity=model.DiagnosticSeverity.Information,
                code="I0001",
                message="This is an information",
            ),
            model.Diagnostic(
                range=model.Range(
                    start=model.Position(line=1, character=10),
                    end=model.Position(line=1, character=14),
                ),
                severity=model.DiagnosticSeverity.Hint,
                code="H0001",
                message="This is a hint",
            ),
        ],
    )

    expected_output = """\
1 | Hello World
    ^^^^^ Error: This is an error

2 | This is a test
    ^^^^ Warning: This is a warning

         ^^ Information: This is an information

              ^^^^ Hint: This is a hint

3 | Thanks bye
"""

    assert str(file) == expected_output


def test_file_str_with_multiline_diagnostics():
    file = model.File(
        path="README.md",
        lines=[
            model.Line(number=1, content="Hello World"),
            model.Line(number=2, content="This is a test"),
            model.Line(number=3, content="Thanks bye"),
        ],
        diagnostics=[
            model.Diagnostic(
                range=model.Range(
                    start=model.Position(line=1, character=0),
                    end=model.Position(line=2, character=10),
                ),
                severity=model.DiagnosticSeverity.Error,
                code="E0001",
                message="This is an error",
            ),
        ],
    )

    expected_output = """\
1 | Hello World
2 | This is a test
    ^^^^^^^^^^^^^^ Error: This is an error

3 | Thanks bye
    ^^^^^^^^^^ Error: This is an error
"""

    assert str(file) == expected_output


def test_insert_lines():
    file = model.File(
        path="file.txt",
        lines=[
            model.Line(number=1, content="Line 1"),
            model.Line(number=2, content="Line 2"),
            model.Line(number=3, content="Line 3"),
        ],
    )

    file = file.insert_lines(start_line=2, content="Line 4\nLine 5")

    expected_output = """\
1 | Line 1
2 | Line 4
3 | Line 5
4 | Line 2
5 | Line 3
"""

    assert str(file) == expected_output


def test_insert_lines_with_empty_file():
    file = model.File(
        path="file.txt",
        lines=[],
    )

    file = file.insert_lines(start_line=1, content="Line 1\nLine 2")

    expected_output = """\
1 | Line 1
2 | Line 2
"""

    assert str(file) == expected_output


def test_insert_lines_after_last_line():
    file = model.File(
        path="file.txt",
        lines=[
            model.Line(number=1, content="Line 1"),
            model.Line(number=2, content="Line 2"),
            model.Line(number=3, content="Line 3"),
        ],
    )

    file = file.insert_lines(start_line=4, content="Line 4\nLine 5")

    expected_output = """\
1 | Line 1
2 | Line 2
3 | Line 3
4 | Line 4
5 | Line 5
"""

    assert str(file) == expected_output


def test_replace_line():
    file = model.File(
        path="file.txt",
        lines=[
            model.Line(number=1, content="Line 1"),
            model.Line(number=2, content="Line 2"),
            model.Line(number=3, content="Line 3"),
        ],
    )

    file = file.replace_lines(start_line=2, end_line=3, content="Line 4")

    expected_output = """\
1 | Line 1
2 | Line 4
3 | Line 3
"""

    assert str(file) == expected_output


def test_replace_line_with_multiline_content():
    file = model.File(
        path="file.txt",
        lines=[
            model.Line(number=1, content="Line 1"),
            model.Line(number=2, content="Line 2"),
            model.Line(number=3, content="Line 3"),
        ],
    )

    file = file.replace_lines(start_line=2, end_line=3, content="Line 4\nLine 5")

    expected_output = """\
1 | Line 1
2 | Line 4
3 | Line 5
4 | Line 3
"""

    assert str(file) == expected_output


def test_replace_lines():
    file = model.File(
        path="file.txt",
        lines=[
            model.Line(number=1, content="Line 1"),
            model.Line(number=2, content="Line 2"),
            model.Line(number=3, content="Line 3"),
        ],
    )

    file = file.replace_lines(start_line=2, end_line=4, content="Line 4\nLine 5")

    expected_output = """\
1 | Line 1
2 | Line 4
3 | Line 5
"""

    assert str(file) == expected_output


def test_replace_lines_with_less_lines():
    file = model.File(
        path="file.txt",
        lines=[
            model.Line(number=1, content="Line 1"),
            model.Line(number=2, content="Line 2"),
            model.Line(number=3, content="Line 3"),
        ],
    )

    file = file.replace_lines(start_line=2, end_line=4, content="Line 4")

    expected_output = """\
1 | Line 1
2 | Line 4
"""
    assert str(file) == expected_output


def test_replace_lines_with_more_lines():
    file = model.File(
        path="file.txt",
        lines=[
            model.Line(number=1, content="Line 1"),
            model.Line(number=2, content="Line 2"),
            model.Line(number=3, content="Line 3"),
        ],
    )

    file = file.replace_lines(
        start_line=2, end_line=4, content="Line 4\nLine 5\nLine 6"
    )

    expected_output = """\
1 | Line 1
2 | Line 4
3 | Line 5
4 | Line 6
"""

    assert str(file) == expected_output


def test_replace_lines_with_empty_file():
    file = model.File(
        path="file.txt",
        lines=[],
    )

    file = file.replace_lines(start_line=1, end_line=2, content="Line 1\nLine 2")

    expected_output = """\
1 | Line 1
2 | Line 2
"""

    assert str(file) == expected_output


def test_replace_lines_with_start_line_after_last_line():
    file = model.File(
        path="file.txt",
        lines=[
            model.Line(number=1, content="Line 1"),
            model.Line(number=2, content="Line 2"),
            model.Line(number=3, content="Line 3"),
        ],
    )

    file = file.replace_lines(start_line=4, end_line=5, content="Line 4\nLine 5")

    expected_output = """\
1 | Line 1
2 | Line 2
3 | Line 3
4 | Line 4
5 | Line 5
"""

    assert str(file) == expected_output


def test_replace_lines_with_end_line_before_first_line():
    file = model.File(
        path="file.txt",
        lines=[
            model.Line(number=1, content="Line 1"),
            model.Line(number=2, content="Line 2"),
            model.Line(number=3, content="Line 3"),
        ],
    )

    with pytest.raises(AssertionError):
        file = file.replace_lines(start_line=1, end_line=0, content="Line 4\nLine 5")


def test_append_lines():
    file = model.File(
        path="file.txt",
        lines=[
            model.Line(number=1, content="Line 1"),
            model.Line(number=2, content="Line 2"),
            model.Line(number=3, content="Line 3"),
        ],
    )

    file = file.append_lines("Line 4\nLine 5")

    expected_output = """\
1 | Line 1
2 | Line 2
3 | Line 3
4 | Line 4
5 | Line 5
"""

    assert str(file) == expected_output


def test_append_lines_with_empty_file():
    file = model.File(
        path="file.txt",
        lines=[],
    )

    file = file.append_lines("Line 1\nLine 2")

    expected_output = """\
1 | Line 1
2 | Line 2
"""

    assert str(file) == expected_output
