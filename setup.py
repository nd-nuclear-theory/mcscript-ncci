from setuptools import setup, find_packages

setup(
    name="mcscript-ncci",
    version="1.0.1",
    author="Mark A. Caprio, Patrick J. Fasano, University of Notre Dame",
    description=("Scripting for NCCI runs"),
    license="MIT",
    packages=find_packages(include="ncci*"),
    python_requires='>=3.8',
    install_requires=[
        "deprecated>=1.2.10",
        "mcscript>=1.0.0",
        "am",
        "mfdnres>=1.0.0",
    ],
    classifiers=[],
)
