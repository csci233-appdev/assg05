import pytest
from q01 import convert_date_format


def test_basic_conversion():
    new_date = convert_date_format('03/12/1998')
    assert new_date == 'March 12, 1998'

    new_date = convert_date_format('12/24/1988')
    assert new_date == 'December 24, 1988'


def test_leading_zero():
    # we don't expect leading 0's to cause a problem or not
    new_date = convert_date_format('9/8/2010')
    assert new_date == 'September 8, 2010'

    new_date = convert_date_format('09/08/2010')
    assert new_date == 'September 8, 2010'

    new_date = convert_date_format('003/9/01968')
    assert new_date == 'March 9, 1968'


def test_old_years():
    # we expect years to not have any assumption about being in the 20th
    # century
    new_date = convert_date_format('6/7/8')
    assert new_date == 'June 7, 8'

    new_date = convert_date_format('10/08/432')
    assert new_date == 'October 8, 432'


def test_space_splits():
    # we expect in fact that using string split and assumption of integer
    # month / day / year, that extra spaces won't be a problem
    new_date = convert_date_format('11  /22 /  1492')
    assert new_date == 'November 22, 1492'

    new_date = convert_date_format('  4  / 13 /  777')
    assert new_date == 'April 13, 777'


def test_bad_delimiters():
    # conversely, if using string split with `/` delimiter, we expect
    # errors for the following
    with pytest.raises(Exception) as excinfo:
        new_date = convert_date_format('11-22-1492')
    assert "invalid literal for int()" in str(excinfo.value)

    with pytest.raises(Exception) as excinfo:
        new_date = convert_date_format('4 5 678')
    assert "invalid literal for int()" in str(excinfo.value)
