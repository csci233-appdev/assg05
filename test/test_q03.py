import pytest
import subprocess
from q03 import character_analysis

text1 = """Now is the time for all good men
to come to the aid of their country.
4 Score and 7 years ago, our father's brought forth
a new nation..."""


def test_simple_analysis():
    # we expect a tuple of analysis results in order
    # (num_char, num_word, num_line, num_upper, num_lower, num_digit, num_whitespace)
    analysis = character_analysis('aB1 cD2')
    assert analysis == (7, 2, 1, 2, 2, 2, 1)

    # there are 3 lines here, tabs are not new lines
    analysis = character_analysis('xXyY89 \naA\tbB\n12')
    assert analysis == (16, 4, 3, 4, 4, 4, 4)


def test_multiline_analysis():
    # more complex, use multiline strings
    analysis = character_analysis(text1)
    assert analysis == (137, 29, 4, 2, 99, 2, 28)


def test_q03_application():
    command = ['python3', 'test/test-question.py', 'q03_application.py']
    result = subprocess.run(command)
    assert result.returncode == 0
