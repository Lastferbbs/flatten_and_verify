from setuptools import setup

setup(
    name="flatten_and_verify",
    version="0.5.0",
    description="Module to automate solidity contract verification with pretty flattening (every file separated on blockexplorer). Code is a modified brownie built flattener and verify.",
    url="https://github.com/Lastferbbs/flatten_and_verify",
    author="Jakub Antkiewicz",
    author_email="antkiewicz.jakub@gmail.com",
    license="MIT",
    packages=["flatten_and_verify"],
    install_requires=[
        "requests>=2.26.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development",
    ],
)
