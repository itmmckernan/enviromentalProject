import os
from setuptools import setup, Extension

module = Extension('cancerMerged', sources=['cancerMerged.cpp'], language='c++')

setup(name='cancerMerged', ext_modules = [module])