import inspect
import ncci
from setuptools import setup

setup(
    name="ncci",
    version="0.0.1",
    author="Mark A. Caprio, Patrick J. Fasano, University of Notre Dame",
    author_email="Mark Caprio <mcaprio@nd.edu>",
    description=("Scripting for NCCI runs"),
    license="MIT",
    packages=['ncci'],
    long_description=inspect.getdoc(ncci),
    classifiers=[],
)
