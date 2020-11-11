#!/usr/bin/env python

import os
import sys
from setuptools import setup

HERE_PATH = os.path.abspath(os.path.dirname(__file__))
ABOUT = {}
with open(os.path.join(HERE_PATH, "csvmedkit", "__about__.py"), "r") as f:
    exec(f.read(), ABOUT)

with open("README.rst", "r") as f:
    README = f.read()

install_requires = [
    "csvkit",
    "python-slugify>=4.0",
    "regex>=2020.7.14",
]

dev_requires = [
    "coverage>=4.4.2",
    "nose>=1.1.2",
    "parameterized",
    "sphinx>=1.0.7",
    "sphinx_rtd_theme",
    "tox>=3.1.0",
]


setup(
    name=ABOUT["__title__"],
    version=ABOUT["__version__"],
    description=ABOUT["__description__"],
    author=ABOUT["__author__"],
    author_email=ABOUT["__author_email__"],
    url=ABOUT["__url__"],
    long_description=README,
    long_description_content_type="text/x-rst",
    project_urls={
        "Documentation": "https://csvmedkit.readthedocs.io/en/latest/",
    },
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    packages=[
        "csvmedkit",
    ],
    entry_points={
        "console_scripts": [
            "csvflatten = csvmedkit.utils.csvflatten:launch_new_instance",
            "csvheader  = csvmedkit.utils.csvheader:launch_new_instance",
            "csvnorm    = csvmedkit.utils.csvnorm:launch_new_instance",
            "csvpivot   = csvmedkit.utils.csvpivot:launch_new_instance",
            "csvsed     = csvmedkit.utils.csvsed:launch_new_instance",
            "csvslice   = csvmedkit.utils.csvslice:launch_new_instance",

        ]
    },
    install_requires=install_requires,
    extras_require={"dev": dev_requires},
)
