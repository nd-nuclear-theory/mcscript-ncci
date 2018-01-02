from setuptools import setup

setup(
    name="mcscript-ncci",
    version="0.0.1",
    author="Mark A. Caprio, Patrick J. Fasano, University of Notre Dame",
    description=("Scripting for NCCI runs"),
    license="MIT",
    packages=['ncci'],
    install_requires=[
        "mcscript>=0.0.1",
    ],
    classifiers=[],
)
