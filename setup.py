import inspect
import ncci
from setuptools import setup

setup(
    name="ncci",
    version="0.0.1",
    author="Mark A. Caprio, Patrick J. Fasano, University of Notre Dame",
    description=("Scripting for NCCI runs"),
    license="MIT",
    packages=['ncci'],
    install_requires=[
        "mcscript>=0.0.1",
    ],
    long_description=inspect.getdoc(ncci),
    classifiers=[],
)
