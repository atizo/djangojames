from distutils.core import setup
import os
from distutils.command.install_data import install_data
from distutils.command.install import INSTALL_SCHEMES

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

ch_dir = os.path.dirname(__file__)
if ch_dir != '':
    os.chdir(ch_dir)

for dirpath, dirnames, filenames in os.walk(root_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

# Tell distutils not to put the data_files in platform-specific installation
# locations. See here for an explanation:
# http://groups.google.com/group/comp.lang.python/browse_thread/thread/35ec7b2fed36eaec/2105ee4d9e8042cb
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

setup(
    name='djangojames',
    version='0.3',
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