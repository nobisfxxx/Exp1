from setuptools import setup, Extension
from Cython.Build import cythonize

extensions = [
    Extension('bot', ['bot.py'])  # Adjust as needed
]

setup(
    ext_modules=cythonize(extensions)
)
