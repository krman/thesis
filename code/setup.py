#!/usr/bin/python

from distutils.core import setup, Command
import codecs
import os

class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys,subprocess
        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)

def read(*paths):
    with codecs.open(os.path.join(*paths), 'r', 'utf-8') as f:
        return f.read()

setup(
    name = 'mcfpox',
    packages = [
	'mcfpox',
	'mcfpox.controller',
	'mcfpox.objectives',
	'mcfpox.topos',
	'mcfpox.experiments',
	'mcfpox.test',
	'mcfpox.test.controller',
	'mcfpox.test.objectives',
	'mcfpox.test.topos'
    ],
    version = '0.1.0',
    description = 'MCF modules for POX',
    long_description = read('README.rst'),
    author = 'Kimberley Manning',
    author_email = 'kmanning@gmx.com',
    url = 'http://krman.github.io/mcfpox',
    license = 'Apache License 2.0',
    classifiers = [
	'Programming Language :: Python',
	'License :: OSI Approved :: Apache Software License'
    ],
    cmdclass = {'test': PyTest},
)
