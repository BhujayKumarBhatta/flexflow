#! venv/bin/python

# -*- coding: utf-8 -*-

import os
import sys
import argparse

possible_topdir = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                                os.pardir,
                                                os.pardir))
apppath = (os.path.join(possible_topdir,
                               'flexflow',
                               'flexflow'))

sys.path.insert(0, apppath)

from flexflow.app_run import main

if __name__ == '__main__':
	main()