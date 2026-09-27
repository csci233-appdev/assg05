import pytest
import subprocess
from q02 import text_to_morse_code


def test_punctuation():
    # ensure the three punctuation and space are all encoded as required
    morse_code = text_to_morse_code(' , . ? ')
    assert morse_code == ' --..-- .-.-.- ..--.. '


def test_digits():
    # ensure all digits are correctly encoded
    morse_code = text_to_morse_code('0123456789')
    assert morse_code == '-----.----..---...--....-.....-....--...---..----.'


def test_characters():
    # ensure all upper case and lower case characters are encoded
    morse_code = text_to_morse_code('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    assert morse_code == '.--...-.-.-.....-.--........----.-.-..---.---.--.--.-.-....-..-...-.---..--.---..'

    # ensure all upper case and lower case characters are encoded
    morse_code = text_to_morse_code('abcdefghijklmnopqrstuvwxyz')
    assert morse_code == '.--...-.-.-.....-.--........----.-.-..---.---.--.--.-.-....-..-...-.---..--.---..'


def test_ignored_characters():
    # ensure function silently ignores other characters not in Morse
    # code table given for the problem
    morse_code = text_to_morse_code('0)1!2@3#4$5%6^7&8*9(-=+')
    assert morse_code == '-----.----..---...--....-.....-....--...---..----.'


def test_basic_conversion():
    # tests of basic messages, don't require handling lower case or
    # unknown characters
    morse_code = text_to_morse_code('SOS')
    assert morse_code == '...---...'

    morse_code = text_to_morse_code(
        'NOW IS THE TIME, FOR ALL GOOD MEN. TO COME TO THE AID OF THEIR COUNTRY?')
    assert morse_code == '-.---.-- ..... -..... -..--.--..-- ..-.---.-. .-.-...-.. --.-------.. --.-..-.-.- ---- -.-.-----. ---- -..... .-..-.. ---..-. -........-. -.-.---..--.-.-.-.-..--..'

    morse_code = text_to_morse_code(
        '4 SCORE AND 7 YEARS AGO, OUR FATHERS BROUGHT FORTH A NEW NATION.')
    assert morse_code == '....- ...-.-.---.-.. .--.-.. --... -.-..-.-.... .---.-----..-- ---..-.-. ..-..--......-.... -....-.---..---.....- ..-.---.-.-.... .- -...-- -..--..----..-.-.-'


def test_tougher_conversion():
    # same basic messages, but with mixed case and non-Morse characters
    morse_code = text_to_morse_code('sos')
    assert morse_code == '...---...'

    morse_code = text_to_morse_code(
        'Now is the time, For All Good Men. To come TO tHE aid OF Their country!#?')
    assert morse_code == '-.---.-- ..... -..... -..--.--..-- ..-.---.-. .-.-...-.. --.-------.. --.-..-.-.- ---- -.-.-----. ---- -..... .-..-.. ---..-. -........-. -.-.---..--.-.-.-.-..--..'

    morse_code = text_to_morse_code(
        '4 score and 7 Years AGO,# our Fathers brought forth A New Nation."|')
    assert morse_code == '....- ...-.-.---.-.. .--.-.. --... -.-..-.-.... .---.-----..-- ---..-.-. ..-..--......-.... -....-.---..---.....- ..-.---.-.-.... .- -...-- -..--..----..-.-.-'


def test_q02_application():
    command = ['python3', 'test/test-question.py', 'q02_application.py']
    result = subprocess.run(command)
    assert result.returncode == 0
