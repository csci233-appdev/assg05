import pytest
import subprocess
from q04 import word_counts


text1 = """Now is the time for all good men
to come to the aid of their country.
4 Score and 7 years ago, our father's brought forth
a new nation..."""


def test_simple_analysis():
    # check a simple string, don't need lower case nor ignore nonalphabetic
    words = word_counts('this is a small sentence')
    assert len(words) == 5
    assert words['this'] == 1
    assert words['is'] == 1
    assert words['a'] == 1
    assert words['small'] == 1
    assert words['sentence'] == 1


def test_simple_counts():
    # check that is counting repeated words
    words = word_counts('this is a small sentence this small a a is is is is')
    assert len(words) == 5
    assert words['this'] == 2
    assert words['is'] == 5
    assert words['a'] == 3
    assert words['small'] == 2
    assert words['sentence'] == 1


def test_basic_word_tokenization():
    # check ignoring all nonalphabetic characters in tokenization
    words = word_counts(
        'Now is tHe time4, all good men! 2come 2the aid OF Their COUNTRY!')
    assert len(words) == 12
    assert words['now'] == 1
    assert words['is'] == 1
    assert words['the'] == 2
    assert words['time'] == 1
    assert words['all'] == 1
    assert words['good'] == 1
    assert words['men'] == 1
    assert words['come'] == 1
    assert words['aid'] == 1
    assert words['of'] == 1
    assert words['their'] == 1
    assert words['country'] == 1


def test_multiline_analysis():
    # more complex, use multiline strings
    words = word_counts(text1)
    assert len(words) == 25
    assert words['the'] == 2
    assert words['to'] == 2
    assert words['nation'] == 1
    assert words['now'] == 1
    assert 'Now' not in words
    assert words['fathers'] == 1
    assert 'father' not in words


def test_q04_application():
    command = ['python3', 'test/test-question.py', 'q04_application.py']
    result = subprocess.run(command)
    assert result.returncode == 0
