#!/usr/bin/env python3
# -*- coding:Utf-8 -*-

# Copyright (c) 2014 "OKso http://okso.me"
#
# This file is part of Skink.
#
# Intercom is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup
from skink import __version__

setup(name='Skink',
      version=__version__,
      description='Control the DOM from Python using Websockets',
      author='OKso.me',
      author_email='@okso.me',
      url='https://github.com/oksome/Skink/',
      packages=['skink'],
      package_data={'skink': ['static/index.html',
                              'static/skink.js',
                              'static/style.css']},
      install_requires=['tornado', 'bottle'],
      license='AGPLv3',
      keywords="websockets javascript injection dom",
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Web Environment',
                   'Programming Language :: Python :: 3',
                   'Operating System :: POSIX',
                   'Operating System :: MacOS :: MacOS X',
                   'Intended Audience :: End Users/Desktop',
                   'Intended Audience :: Information Technology',
                   'License :: OSI Approved :: GNU Affero General Public License v3',
                   'Topic :: Home Automation',
                   'Topic :: Scientific/Engineering :: Human Machine Interfaces',
                   'Topic :: Scientific/Engineering :: Visualization',
                   ],
      )
