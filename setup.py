#!/usr/bin/env python
from setuptools import setup

setup(
    name='nameko-ari',
    version='1.0',
    description='Nameko Asterisk Restfull API (ARI) extension',
    author='Max Lit',
    author_email='max.lit.mbox@gmail.com',
    url='http://github.com/litnimax/nameko-ari',
    py_modules=['nameko_ari'],
    install_requires=[
        "nameko>=2.5.1",
        "bravado",
    ],
    packages=('nameko_ari',),
    package_dir={'nameko_ari': 'nameko_ari'},
    extras_require={
        'dev': [
            "coverage==4.0.3",
            "flake8==3.3.0",
            "pylint==1.8.2",
            "pytest==2.8.3",
        ]
    },
    zip_safe=True,
    license='Apache License, Version 2.0',
    classifiers=[
        "Programming Language :: Python",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
    ]
)
