"""
A minimal setup.py.
"""
from setuptools import setup, find_packages

setup(
    name="feed_aggregation",
    install_requires=["attrs", "hyperlink", "Klein", "feedparser", "lxml", "treq"],
    package_dir={"": "src"},
    packages=find_packages("src") + ["twisted.plugins"],
)
