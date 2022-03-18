import setuptools
from ubxlib._version import __version__ as version


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="ubxlib",
    version=version,
    author="Rene Straub",
    author_email="straub@see5.ch",
    description="ublox gnss library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/renestraub/ubxlib",
    packages=setuptools.find_packages(exclude=("tests",)),
    classifiers=[
        'Programming Language :: Python :: 3.7',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
