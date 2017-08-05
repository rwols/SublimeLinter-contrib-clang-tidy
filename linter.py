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
import sublime
from SublimeLinter.lint import Linter, util


class ClangTidy(Linter):
    """Provides an interface to clang-tidy."""

    syntax = ('c', 'c++', 'objective-c', 'objective-c++')
    executable = 'clang-tidy'
    version_args = '-version'
    version_re = r'(?P<version>\d+\.\d+\.\d+)'
    version_requirement = '>= 3.0'
    regex = (
        r'^.+?:(?P<line>\d+):(?P<col>\d+): '
        r'(?:(?P<error>error)|(?P<warning>warning)): '
        r'(?P<message>.+)'
    )
    multiline = False
    line_col_base = (1, 1)
    tempfile_suffix = '-'
    error_stream = util.STREAM_BOTH
    selectors = {}
    word_re = None
    defaults = {}
    inline_settings = None
    inline_overrides = None
    comment_re = None
    config_file = ('.clang-tidy')
    word_re = r'^([-\w:#]+)'

    def cmd(self):
        settings = self.view.settings()
        compile_commands = settings.get("compile_commands", "")
        vars = self.view.window().extract_variables()
        compile_commands = sublime.expand_variables(compile_commands, vars)
        compdb = os.path.join(compile_commands, "compile_commands.json")
        if not os.path.isfile(compdb):
            return None
        return [self.executable, "-p={}".format(compile_commands), "-config=", self.view.file_name()]
