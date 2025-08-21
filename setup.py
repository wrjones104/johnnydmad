from setuptools import setup, find_packages

setup(
    name='johnnydmad',
    version='0.1.0',
    packages=find_packages(where='.'),
    install_requires=[
        'numpy',
        'mfvitools',
        'PyYAML'
    ],
    package_data={'': ['*.txt', '*.dat']},
    include_package_data=True,
)
