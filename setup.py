from setuptools import setup, find_packages

setup(
    name='johnnydmad',
    version='0.1.0',
    package_dir={'johnnydmad': ''},
    packages=find_packages(where='.'),
    install_requires=[
        'numpy',
        'PyYAML'
    ],
    package_data={'': ['*.txt', '*.dat']},
    include_package_data=True,
)
