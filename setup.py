from setuptools import setup
import os

packages = []
data_files = []
root_dir = 'djangojames'

def fullsplit(path, result=None):
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)


for dirpath, dirnames, filenames in os.walk(root_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

setup(
    name='djangojames',
    version='0.2',
    description="Helpers and tools for django",
    author='Marcel Eyer',
    author_email='me@maersu.ch',
    url='https://github.com/atizo/djangojames',
    packages=packages,
    data_files=data_files,
    zip_safe=False,
    install_requires=[
        'python-googleanalytics',
    ],    
)