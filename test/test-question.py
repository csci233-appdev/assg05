#!/usr/bin/env python
#
# Command line script to test an assignment question.  This 
# command will run some number of input/output tests for a
# given question solution.  Output is compared using diff with
# expected correct output, and results of running tests are
# reported and a exit value code of 0 is returned if all tests
# are successful, and non-zero to indicate a failure of some or
# all of the tests.
import argparse
import itertools
import os
import subprocess
import sys

# constants for colored terminal output (https://misc.flogisoft.com/bash/tip_colors_and_formatting)
GREEN="\033[1m\033[92m" # this is actually bold light green
RED="\033[1m\033[91m"   # bold light red
BLUE="\033[1m\033[34m"  # default blue
NORMAL="\033[0m"


def parse_args():
    """
    Define and parse the command script command line arguments.  Returns
    the resulting args parsed by the standard python
    argparse.ArgumentParser

    Returns
    -------
    args: A argparse NameSpace dictionary
      All command line argument values that were parsed from the command
      line are set and verified by this function.

    Exception
    ---------
    On error or using the -h | --help flag, this function will exit and
    display an error or usage message.
    """
    # define command line arguments
    parser = argparse.ArgumentParser(
        description='Run one or more defined tests for an assignment question. '
                    'Each question has one or more tests defined for it.  Your '
                    'answer is run and given a set of input, and your output will '
                    'be checked against a set of expected correct output.  If your '
                    'output matches the correct output, your solution passes, if not '
                    'it fails.')
    parser.add_argument('question_script',
        help='The full path to the question solution script to be tested, for '
             'example "q01.py", the answre for question 01 in the current '
             'directory.')
    parser.add_argument('testnum', type=int, default=0, nargs='?',
        help='The question test number to run.  Tests are numbered 1..N for '
             'a given question.  If only this argument is provided, only that '
             'test number will be run for the question.  If neither optional '
             'arguments are provided, all tests for the question are run.')
    parser.add_argument('endtestnum', type=int, default=0, nargs='?',
        help='If both a begin [testnum] and [endtestnum] are provided, the '
             'tests ranging from testnum to endtestnum will be run.')
    parser.add_argument('-c', '--color', action='store_true', default=False,
        help='Color the test result output, red for failed tests, green '
             'for successful tests.')
    parser.add_argument('-t', '--tee', action='store_false', default=True,
        help='Do not Tee standard input to allow redirected file input to show '
             'in the output results for tests. By default we add in code to '
             'correct the output displayed when using python input() statements '
             'but if this should be suppressed, disable it using this option.')
    parser.add_argument('--test_directory', default='./test')
    parser.add_argument('--output_directory', default='./output')

    # parse the command line arguments
    args = parser.parse_args()

    # set global settings based on argument flags
    # if not using terminal output colors, just empty string the color
    # terminal settings so nothing happens when used
    if not args.color:
        args.GREEN = ''
        args.RED = ''
        args.BLUE = ''
        args.NORMAL = ''
    else:
        args.GREEN = GREEN
        args.RED = RED
        args.BLUE = BLUE
        args.NORMAL = NORMAL

    # ensure that the output directory exists to place output from test
    # runs into
    if not os.path.exists(args.output_directory):
        os.makedirs(args.output_directory)

    # run some error checks, first ensure that the asked for question
    # script file to be tested exists
    if not os.path.exists(args.question_script):
        print(f'test-question.py: error: could not open question script file <{args.question_script}>',
              file=sys.stderr)
        sys.exit(1)
    else:
        # otherwise for convenience determine the basename / prefix of the
        # question answer script we will be running tests for
        args.question_prefix, _ = os.path.splitext(os.path.basename(args.question_script))

    # Now determine the range of question tests to run are correct, or if
    # not specified determine the actual begin and end question tests
    # make sure that the starting test exists
    if args.testnum != 0:
        _, _, _ = get_test_files(args, args.testnum)

    # make sure the ending test asked for exists
    if args.endtestnum != 0:
        _, _, _ = get_test_files(args, args.endtestnum)
    
    # if only start was asked for, and we know that test exists, set
    # the end test range so we only run the single asked for test
    if args.testnum != 0 and args.endtestnum == 0:
        args.endtestnum = args.testnum

    # if no test range was specified, discover all of the tests and default
    # to running all of them
    if args.testnum == 0 and args.endtestnum == 0:
        # TODO: we are assuming there is always 1 test, and we just
        # loop through until we find N test number that does not exist
        args.testnum = 1
        next_testnum = 2
        input_file, _, _ = get_test_files(args, next_testnum, test=False)
        while os.path.exists(input_file):
            next_testnum += 1
            input_file, _, _ = get_test_files(args, next_testnum, test=False)
        args.endtestnum = next_testnum - 1

    # return the parsed and error checked command line arguments
    return args


def get_test_files(args, testnum, test=True):
    """
    Convenience method to determine the name of the test input file and
    expected output file.  We construct this path name many times in
    this code, so put logic in one place. For example we may need to add
    more flexibility to specify a path where the test file are located
    in future.

    Parameters
    ----------

    args: An argparse namespace dictionary.
        We expect that the correct args.question_prefix and
        args.test_directory are set in this dictionary indicating the
        location of the test files and the name of the question script
        we will generate input and expected output file names for.
    testnum - The particular test number we need input and expected
        output for.

    Returns
    -------
    input_file, expected_output_file, output_file: str, str, stru
        A tuple of the path name to the input file, the expected
        output file and the actual output_file to be used for this test.

    Exceptions
    ----------
    This method will print an error message and return exit status of 1
    (error) if the asked for file does not actually exist.
    """
    input_file = f'{args.test_directory}/data/{args.question_prefix}-{testnum:02d}-input.dat'
    expected_output_file = f'{args.test_directory}/data/{args.question_prefix}-{testnum:02d}-expected.out'
    output_file = f'{args.output_directory}/{args.question_prefix}-{testnum:02d}-actual.out'

    # perform error checking, the error here usually means an invalid test number
    # has been asked for
    if test and not os.path.exists(input_file):
        print(f'test-question.py: error: invalid test number: {testnum:02d}', file=sys.stderr)
        print(f'                  file not found <{input_file}>', file=sys.stderr)
        sys.exit(1)
    if test and not os.path.exists(expected_output_file):
        print(f'test-question.py: error: invalid test number: {testnum:02d}', file=sys.stderr)
        print(f'                  file not found <{expected_output_file}>', file=sys.stderr)
        sys.exit(1)

    # success, the input and expected output exist
    return input_file, expected_output_file, output_file


def remove_repeated_whitespace(lines):
    """
    Remove repeated whitespace in a list of string lines / output.
    Also remove any lines that are completely blank, this makes
    extra newlines in or at end of output to be ignored.

    Parameters
    ----------
    lines : list of str
      A regular python list of strings of the original whole output
      generated by a run of a user question answer.

    Returns
    -------
    clean_lines : list of str
      A new list of strings, all completely blank lines will be removed,
      and all repeated whitespace within a line will be reduced to a single
      space.
    """
    clean_lines = []
    for line in lines:
        clean_line = ' '.join(line.strip().split())
        if clean_line != '':
            clean_lines.append(clean_line)
    return clean_lines


def diff_file_output(args, student_output, expected_output):
    """
    We could use difflib or similar, but we want a simple
    diff method here.  This function returns True if the
    output matches line-to-line, and False if not.  This
    function can ignore repeated whitespace based on the
    global arguments args.ignore_whitespace_changes.

    Parameters
    ----------
    args: An argparse namespace dictionary.
        We expect that the correct args.question_prefix and
        args.test_directory are set in this dictionary indicating the
        location of the test files and the name of the question script
        we will generate input and expected output file names for.
    student_output: list of str
        The output captured from running the student solution for a 
        question.
    expected_output: list of str
        The expected correct output for a question.

    Returns
    -------
    identical: bool
        True if the files are identical when tested, False if not.
    """
    # clean the output by remove all repeated whitespace
    student_output_cleaned = remove_repeated_whitespace(student_output)
    expected_output_cleaned = remove_repeated_whitespace(expected_output)

    return student_output_cleaned != expected_output_cleaned

def report_diff_file_output(args, student_output, expected_output):
    """
    We could use difflib or similar, but we want a simple
    diff method here.  This function returns True if the
    output matches line-to-line, and False if not.  This
    function can ignore repeated whitespace based on the
    global arguments args.ignore_whitespace_changes.

    Parameters
    ----------
    args: 
    student_output: list of str
    expected_output: list of str

    Returns
    -------
    identical: bool
        True if the files are identical when tested, False if not.
    """
    # clean the output by remove all repeated whitespace
    student_output_cleaned = remove_repeated_whitespace(student_output)
    expected_output_cleaned = remove_repeated_whitespace(expected_output)

    linenum = 1
    for student_line, student_line_cleaned, expected_line, expected_line_cleaned in itertools.zip_longest(student_output, student_output_cleaned, expected_output, expected_output_cleaned, fillvalue=''):
        if student_line_cleaned != expected_line_cleaned:
            print(f'{linenum:03d} student:  <{student_line_cleaned.replace('\n', '')}>')
            print(f'{linenum:03d} expected: <{expected_line_cleaned.replace('\n', '')}>')
        linenum += 1
    print('')


def check_test_passed(args, testnum, output_file, expected_output_file):
    """
    Check if a test passes or fails.  This is an input / output diff
    test.  We compare the output to the expected output for differences.
    If no difference in output, test passes.  If output differs, test
    fails.

    Parameters
    ----------
    args: An argparse namespace dictionary.
        We expect that all arguments are present and have been error
        checked at this point, e.g. that the script to test exists, and
        that the start and end test numbers to iterate are present and
        valid tests to run.
    output_file: str
    expected_output_file: str
        Results of test run output are redirected to the `output_file`.
        The corrected expected output for the test are found in the
        `expected_output_file`.
    """
    # open the files and read in all lines
    student_file = open(output_file)
    expected_file = open(expected_output_file)
    if not student_file or not expected_file:
        return False

    student_output = student_file.readlines()
    student_file.close()
    expected_output = expected_file.readlines()
    expected_file.close()

    # if files differ, the test fails and we display failure results
    if diff_file_output(args, student_output, expected_output):
        print(f'Question {args.BLUE}<{args.question_prefix}>{args.NORMAL} Test {args.BLUE}{testnum:02d}{args.NORMAL}: {args.RED} FAILED {args.NORMAL}')
        report_diff_file_output(args, student_output, expected_output)
        return False
    # if files do not differ, test passes
    else:
        print(f'Question {args.BLUE}<{args.question_prefix}>{args.NORMAL} Test {args.BLUE}{testnum:02d}{args.NORMAL}: {args.GREEN} PASSED {args.NORMAL}')
        return True


def run_test(args, testnum):
    """
    Run the individual specific test and report the result pass / fail
    back to the caller.

    This method calls the script file and passes in the input for the
    specific test number.

    The output is saved to the output directory.

    A file diff between the actual output and expected output is
    performed. If the files differ, then the test fails.  If the outputs
    are identical, then the test passes.

    Parameters
    ----------
    args: An argparse namespace dictionary.
        We expect that all arguments are present and have been error
        checked at this point, e.g. that the script to test exists, and
        that the start and end test numbers to iterate are present and
        valid tests to run.
    testnum: int
        The test number to run on the question script.  The presence
        of the script and the test number to run should already have
        been checked to determine they are valid and exist.  In this
        function we run the asked for test and determine if it passes
        or fails.

    Returns
    -------
    passed: bool
        Returns a simple boolean result of True if the test passes, and
        False if it fails.
    """
    # get the file names to use for this test
    input_file, expected_output_file, output_file = get_test_files(args, testnum)

    # read input into a string for the subprocess redirection into its
    # stdin
    with open(input_file, 'r') as f:
        input_data = f.read().encode()

    # read in the students script file into a string so we can run the
    # subprocess as if we are passing a string of commands to the python
    # interpreter
    with open(args.question_script, 'r', encoding='utf-8') as f:
        question_script = f.read()

    # if we are asked to fix the standard output by teeing the input
    # so that python `input()` statements are echoed, read in 
    # the code to create a tee of standard input to prepend to the
    # student solution
    if args.tee:
        tee_script_file = f'{args.test_directory}/tee-script.py'
        with open(tee_script_file, 'r', encoding='utf-8') as f:
            tee_script = f.read()

        question_script = tee_script + "\n\n" + question_script

    # run the command, result is True if the command runs without errors,
    # or False if the subprocess run fails for some reason, e.g. the
    # students solutions throws and exception
    command = ["python3", "-c", question_script]
    with open(output_file, 'w') as out:
        # run the command
        result = subprocess.run(
            command,
            input=input_data,
            stdout=out,
        )

    # now test if the result passed or failed, returncode of 0 indicates
    # the script ran without an error
    if result.returncode == 0:
        return check_test_passed(args, testnum, output_file, expected_output_file)
    else:
        return False


def run_tests(args):
    """
    Run the asked for tests.  This is the main loop that loops through
    all of the tests asked to be run from beginning args.testnum to
    args.endtestnum.  Results are gathered and returned for reporting.
    The actual individual tests are handeled by the run_test() method.

    Parameters
    ----------
    args: An argparse namespace dictionary
        We expect that all arguments are present and have been error
        checked at this point, e.g. that the script to test exists, and
        that the start and end test numbers to iterate are present and
        valid tests to run.

    Returns
    -------
    num_passed, num_attempted: int, int
       A tuple of integer results is returned. The number of tests that
       passed out of the number of tests attempted are reported back
       from the call to this function.
    """
    # iterate over and run all of the tests asked for
    num_passed = 0
    num_attempted = 0
    testnum = args.testnum
    print('')
    while testnum <= args.endtestnum:
        # run the test
        passed = run_test(args, testnum)

        # gather results for reporting
        if passed:
            num_passed += 1
        testnum += 1
        num_attempted += 1

    # report summary results
    print('')
    if num_passed == num_attempted:
        print(f'{args.GREEN}', '='*75, f'{args.NORMAL}')
        print(f'{args.GREEN} All attempted question tests passed {args.NORMAL} ({num_passed:03d} passed of {num_attempted:03d} tests attempted)')
    else:
        print(f'{args.RED}', '='*75, f'{args.NORMAL}')
        print(f'{args.RED} Question test failures detected {args.NORMAL} ({num_passed:03d} passed of {num_attempted:03d} tests attempted)')

    # return results
    return num_passed, num_attempted
    


if __name__ == "__main__":
    # parse the command line arguments
    args = parse_args()
    #print(args)

    # run the asked for tests
    num_passed, num_attempted = run_tests(args)

    # give an exit code of 0 if all tests successful, and non zero
    # count of number of failures otherwise
    if num_passed == num_attempted:
        sys.exit(0)
    else:
        sys.exit(num_attempted - num_passed)
