from setuptools import setup, find_namespace_packages

setup(
    name="mcscript-ncci",
    version="2.0.0",
    author="Mark A. Caprio, Patrick J. Fasano, University of Notre Dame",
    description=("Scripting for NCCI runs"),
    license="MIT",
    packages=find_namespace_packages(include="mcscript.ncci*", exclude=["docs*","scratch*","build*"]),
    python_requires='>=3.8',
    install_requires=[
        "deprecated>=1.2.10",
        "mcscript>=2.0.0",
        "am",
        "mfdnres>=1.0.1",
    ],
    classifiers=[],
)
