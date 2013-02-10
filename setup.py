import os
import sys
from setuptools import setup, find_packages

from tagalog import __version__

requirements = ['redis==2.7.2']

if sys.version_info[:2] < (2, 7):
    requirements.append('argparse')

HERE = os.path.dirname(__file__)
try:
    long_description = open(os.path.join(HERE, 'README.rst')).read()
except:
    long_description = None

setup(
    name='tagalog',
    version=__version__,
    packages=find_packages(exclude=['test*']),
    include_package_data=True,

    # metadata for upload to PyPI
    author='Nick Stenning',
    author_email='nick@whiteink.com',
    url='https://github.com/nickstenning/tagalog',
    description='Tagalog: tools for manipulating, tagging and shipping log data',
    long_description=long_description,
    license='MIT',
    keywords='sysadmin log logging redis tail',

    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'logship=tagalog.command.logship:main',
            'logstamp=tagalog.command.logstamp:main',
            'logtag=tagalog.command.logtag:main',
            'logtext=tagalog.command.logtext:main'
        ]
    }
)
