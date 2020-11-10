#  Copyright (c) 2020 Developer From Jokela.
#  @author developerfromjokela

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='wilma-python-sdk',
    version='0.1.2',
    author="Developer From Jokela",
    author_email="info@developerfromjokela.com",
    description="Python SDK for Wilma API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/developerfromjokela/wilma-python-sdk",
    packages=setuptools.find_packages(),
)
