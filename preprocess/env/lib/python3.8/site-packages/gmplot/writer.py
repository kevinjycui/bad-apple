import warnings
import inspect
from .utility import _INDENT

class _Writer(object):
    '''Writer used to format content with consistent indentation.'''

    def __init__(self, file):
        '''
        Args:
            file (handle): File to write to.
        '''
        self._file = file
        self._indent_level = 0
        self._start_of_line = True

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        '''
        Args:
            exception_type: Type of exception that triggered the exit. 
            exception_value: Value of exception that triggered the exit.
            traceback: Traceback when exit was triggered.
        '''
        # Clear the file if an uncaught exception occured while writing:
        if exception_type:
            self._file.truncate(0)

    def indent(self):
        '''Indent the writer by one level.'''
        self._indent_level += 1
        return self

    def dedent(self):
        '''Dedent the writer by one level.'''
        if self._indent_level > 0:
            self._indent_level -= 1
        else:
            warnings.warn("Can't dedent further!")
            
        return self

    def write(self, content='', end_in_newline=True):
        '''
        Write content.

        Optional:

        Args:
            content (str): Content to write, as a string.
                Content is cleaned using the same rules as Python's ``inspect.cleandoc()``:
                - Leading and trailing empty lines are removed.
                - Any leading whitespace common to all lines is removed.
                - All tabs are expanded to spaces.
            end_in_newline (bool): Whether or not to write a newline at the end. Defaults to True.
        '''
        lines = inspect.cleandoc(content).splitlines()

        # For each line of content...
        for index, line in enumerate(lines):

            # ...indent if the writer is at the start of a line:
            if self._start_of_line:
                self._file.write(_INDENT * self._indent_level)

            # ...write the line:
            self._file.write(line)

            # ...write a newline if there's still more content:
            if index < len(lines) - 1:
                self._file.write('\n')
                self._start_of_line = True

        # If the content should end in a newline, write it:
        if end_in_newline:
            self._file.write('\n')
            self._start_of_line = True
        else:
            self._start_of_line = False
          
        return self
