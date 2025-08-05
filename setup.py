from setuptools import setup, find_packages

setup(
    name="securenet-monitor",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        'watchdog==3.0.0',
        'click==8.1.3',
        'pyyaml==6.0.1',
    ],
    python_requires='>=3.7',
    author='J0shk1ng',
    description='SecureNet File Monitoring System',
    entry_points={
        'console_scripts': [
            'securenet=monitor.cli:cli',
        ],
    },
)