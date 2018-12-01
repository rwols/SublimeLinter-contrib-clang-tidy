#
# linter.py
# Linter for SublimeLinter3, a code checking framework for Sublime Text 3
#
# Written by Raoul Wols
# Copyright (c) 2017 Raoul Wols
#
# License: MIT
#

"""This module exports the ClangTidy plugin class."""

import logging
import os
import re
import sublime
from SublimeLinter.lint import Linter

logger = logging.getLogger('SublimeLinter.clang-tidy')


class ClangTidy(Linter):
    """Provides an interface to clang-tidy."""

    executable = 'clang-tidy'
    regex = (
        r'(^.+?:(?P<line>\d+):(?P<col>\d+): )?'
        r'(?:(?P<error>error)|(?P<warning>warning)): '
        r'(?P<message>.+)'
    )
    tempfile_suffix = '-'
    word_re = r'^([-\w:#]+)'
    defaults = {
        'selector': 'source.c, source.c++, source.objc, source.objc++',
    }

    def cmd(self):
        """Return the actual command to invoke."""
        settings = self.view.settings()
        compile_commands = settings.get("compile_commands", "")
        if not compile_commands:
            logger.error('No "compile_commands" key present in the settings '
                         'of the view.')
            return [self.executable, "-version"]
        vars = self.view.window().extract_variables()
        compile_commands = sublime.expand_variables(compile_commands, vars)
        compdb = os.path.join(compile_commands, "compile_commands.json")
        if os.path.isfile(compdb):
            return [self.executable,
                    "-quiet",
                    "-p={}".format(compile_commands),
                    "-config=",
                    "${args}",
                    "$file"]
        else:
            logger.error('"{}" is not a compilation database.'.format(compdb))
            return [self.executable, "-version"]

    def on_stderr(self, stderr):
        """Filter the output on stderr for actual errors."""
        # Ignore any standard messages. Everything else results in an error.
        stderr = re.sub(r'^\d+.+(warning|error).+generated\.\n', '', stderr)
        stderr = re.sub(r'^Error while processing .+\.\n', '', stderr)

        # show any remaining error
        if stderr:
            self.notify_failure()
            logger.error(stderr)

    def split_match(self, match):
        """Return the components of the error message."""
        match, line, col, error, warning, message, near = \
            super().split_match(match)

        # if the line could not be extracted from the output we set it to the
        # first line to show the message in the error pane
        if line is None:
            line = 0

        return match, line, col, error, warning, message, near
