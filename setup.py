from setuptools import setup, find_packages

setup(
    name="mcscript-ncci",
    version="0.1.2",
    author="Mark A. Caprio, Patrick J. Fasano, University of Notre Dame",
    description=("Scripting for NCCI runs"),
    license="MIT",
    packages=find_packages(include="ncci*"),
    python_requires='>=3.9',
    install_requires=[
        "deprecated>=1.2.10",
        "mcscript>=0.1.0",
        "am",
        "mfdnres",
    ],
    classifiers=[],
)
