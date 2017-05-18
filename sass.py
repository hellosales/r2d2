#!/usr/bin/env python
import os
cwd = os.getcwd()
command = "sass --scss --compass --sourcemap --debug-info --watch --trace %s/r2d2/static/scss/:%s/r2d2/static/.sass-cache/"\
    % (cwd, cwd)

os.system(command)
