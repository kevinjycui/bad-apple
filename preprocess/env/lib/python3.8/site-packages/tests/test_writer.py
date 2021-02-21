import unittest
import warnings
from gmplot.utility import StringIO
from gmplot.writer import _Writer

def _get_comparison_error_message(output, expected_output):
    return """
The following output:
'''%s'''

Doesn't match the expected output:
'''%s'''
""" % (output, expected_output)

class WriterTest(unittest.TestCase):
    def test_writing_lines(self):
        with StringIO() as f:
            with _Writer(f) as writer:
                writer.write("Here's a sample line...").write()
                writer.write('List of random items:')
                writer.indent()
                writer.write('- First')
                writer.write('- Second')
                writer.write('- Third')
            output_string = f.getvalue()

        EXPECTED_OUTPUT = '''\
Here's a sample line...

List of random items:
    - First
    - Second
    - Third
'''

        self.assertEqual(output_string, EXPECTED_OUTPUT, _get_comparison_error_message(output_string, EXPECTED_OUTPUT))

    def test_writing_multilines(self):
        with StringIO() as f:
            with _Writer(f) as writer:
                writer.write('''


                    Here's a sample line...

                    List of random items:
                        - First
                    \t- Second
                        - Third


                ''')
            output_string = f.getvalue()

        EXPECTED_OUTPUT = '''\
Here's a sample line...

List of random items:
    - First
    - Second
    - Third
'''

        self.assertEqual(output_string, EXPECTED_OUTPUT, _get_comparison_error_message(output_string, EXPECTED_OUTPUT))

    def test_extra_dedentation(self):
        with StringIO() as f:
            with _Writer(f) as writer:
                writer.indent().write("Here's a sample indented line...")
                writer.dedent().write("Here's another line before an extra dedent...")

                with warnings.catch_warnings(record=True) as w:
                    warnings.simplefilter("always")

                    writer.dedent()

                    self.assertEqual(len(w), 1, "The extra dedent should raise a single warning")
                    self.assertTrue(issubclass(w[-1].category, UserWarning), "The extra dedent should raise a 'UserWarning'")

                writer.write("And here's a third line after the extra dedent.")
            output_string = f.getvalue()

        EXPECTED_OUTPUT = '''\
    Here's a sample indented line...
Here's another line before an extra dedent...
And here's a third line after the extra dedent.
'''

        self.assertEqual(output_string, EXPECTED_OUTPUT, _get_comparison_error_message(output_string, EXPECTED_OUTPUT))

    def test_exception_exit(self):
        with StringIO() as f:
            try:
                with _Writer(f) as writer:
                    writer.write('Content')
                    raise Exception
                    writer.write('Unreachable content')
            except:
                self.assertEqual(f.getvalue(), '', "The written-to file should be empty if an exception is triggered")
