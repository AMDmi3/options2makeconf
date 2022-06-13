from setuptools import setup, find_packages

setup(
    name='aggregate-port-options',
    version='0.1.0',
    packages=find_packages(include=['aggregate_port_options'])
    entry_points={
        'console_scripts': ['aggregate-port-options=aggregate_port_options:main']
    }
)
