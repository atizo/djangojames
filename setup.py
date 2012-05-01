from setuptools import setup, find_packages

setup(
    name='djangojames',
    version='0.2',
    description="Helpers and tools for django",
    author='Marcel Eyer',
    author_email='me@maersu.ch',
    url='https://github.com/atizo/djangojames',
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        'python-googleanalytics',
    ],    
)