# Extra code to import and place in front of student
# solutions.  When the `input()` built-in is used in Python and
# we redirect standard input from a file, then the input is
# not echoed on the standard output, including a newline the
# interactive user would normally give to send the input.
# The following will recreate the sys.stdin to Tee its input.
# This means all standard input is read in, but also explicitly
# echoed back out to standard output.  This makes it so that
# student solutions using `input()` give normal looking and
# expected output when we redirect input from a file for testing.
import sys
class TeeInput:
    def __init__(self, input_stream, output_stream):
        self.input_stream = input_stream
        self.output_stream = output_stream

    def readline(self):
        line = self.input_stream.readline()
        if line:
            self.output_stream.write(line)
            self.output_stream.flush()
        return line

if not sys.stdin.isatty():
    sys.stdin = TeeInput(sys.stdin, sys.stdout)

