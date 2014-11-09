#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='profile-tools',
    version='0.1',
    url='https://github.com/huanghao/profile-tools',
    author='Huang, Hao',
    author_email='huang1hao@gmail.com',
    packages=find_packages(),
    scripts=[
        'myconf.py',
    ],
    install_requires=[
        'pyYAML',
    ],
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
        ],
    )
