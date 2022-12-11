import re
from setuptools import setup, find_packages


with open('requirements.txt', 'rt') as f:
    REQUIREMENTS = f.readlines()

with open('smartva/__init__.py', 'rt') as f:
    VERSION = re.search("(?<=^version = ').+(?='$)", f.read(), re.M).group()


setup(
    name='smartva',
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    # install_requires=REQUIREMENTS,
    entry_points={
        'console_scripts': [
            'smartva=smartva.va_cli:main',
        ]
    },
    # python_requires='~=2.7',
)
