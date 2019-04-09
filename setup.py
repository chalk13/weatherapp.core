from setuptools import setup, find_namespace_packages

setup(
    name="weatherapp.core",
    version="0.1.0",  # MAJOR.MINOR.PATCH
    author="Artem Mazur",
    description="A simple weather aggregator",
    long_description="",
    packages=find_namespace_packages(),
    entry_points={
        'console_scripts': 'wfapp=weatherapp.core.app:main'
    },
    install_requires=[
        'bs4',
        'requests',
        'colorlog',
        'prettytable',
    ]
)