# mcscript-ncci installation #
Prerequisites: `mcscript`, `shell`

# 1. Retrieving source

  Change to the directory where you want the repository to be installed,
  e.g.,
  ~~~~~~~~~~~~~~~~
  % cd ~/code
  ~~~~~~~~~~~~~~~~

  Clone the `mcscript-ncci` repository and all submodules.
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  % git clone https://github.com/nd-nuclear-theory/mcscript-ncci.git
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  Change your working directory to the repository for the following steps:
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  % cd mcscript-ncci
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  If you want the bleeding-edge, potentially broken version, check out the
  `develop` branch:
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  % git checkout -t origin/develop
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  Setup the package in your `PYTHONPATH` by running `pip` (or `pip3` on Debian):
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  % pip install --user --editable .
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  This will ***fail*** if you have not already installed `mcscript`. If this
  happens, go back and ensure that `mcscript` has been installed successfully.

  a. Subsequently updating source
  ~~~~~~~~~~~~~~~~
  % git pull
  % pip install --user --editable .
  ~~~~~~~~~~~~~~~~

# 2. Environment Configuration

  The environment variable `NCCI_DATA_DIR_H2` is used to tell `mcscript-ncci`
  where to find interaction TBME files.  The scripting will search for TBME
  files in the directory given by `NCCI_DATA_DIR_H2`.  This may also be given as
  a colon-separated list of directories to search.  More precisely, TBME files
  are expected to live in subdirectories, following the naming convention:
  ```<interaction_group>/<interaction_name>-<ob|tb>-<N1bmax|N2bmax>-<hw>.bin```

  #### @NDCRC: ####
  `.cshrc`:
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # mcscript-ncci
  setenv NCCI_DATA_DIR_H2 "/afs/crc.nd.edu/group/nuclthy/data/h2"
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  `.bashrc` or `.bash_profile`:
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # mcscript-ncci
  export NCCI_DATA_DIR_H2="/afs/crc.nd.edu/group/nuclthy/data/h2"
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  #### @NERSC: ####
  `.cshrc`:
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # mcscript-ncci
  setenv NCCI_DATA_DIR_H2 "/global/cfs/cdirs/m2032/data/h2"
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  `.bashrc` or `.bash_profile`:
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # mcscript-ncci
  export NCCI_DATA_DIR_H2="/global/cfs/cdirs/m2032/data/h2"
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  If you use `mcscript-ncci` to postprocess wave functions, you also need to set
  the environment variable `NCCI_LIBRARY_PATH`, to tell `mcscript-ncci` where to
  find the results of prior runs (results files, wave function files, and other
  files containing metadata about the run).  This may also be given as a
  colon-separated list of directories to search.