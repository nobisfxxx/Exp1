from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("cy_device_spoofing.pyx", language_level="3")
)
