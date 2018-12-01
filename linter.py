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

import os
import re
import sublime
from SublimeLinter.lint import Linter


class ClangTidy(Linter):
    """Provides an interface to clang-tidy."""

    executable = 'clang-tidy'
    regex = (
        r'^.+?:(?P<line>\d+):(?P<col>\d+): '
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
            print("SublimeLinter-contrib-clang-tidy: error: no "
                  '"compile_commands" key present in the settings of the '
                  "view.")
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
            print("SublimeLinter-contrib-clang-tidy: error: "
                  '"{}" is not a compilation database.'.format(compdb))
            return [self.executable, "-version"]

    def on_stderr(self, stderr):
        """Filter the output on stderr for actual errors."""
        # Ignore any standard messages. Everything else results in an error.
        stderr = re.sub(r'^\d+.+(warning|error).+generated\.\n', '', stderr)
        stderr = re.sub(r'^Error while processing .+\.\n', '', stderr)

        # show any remaining error
        if stderr:
            self.notify_failure()
            print("SublimeLinter-contrib-clang-tidy: error: " + stderr)
