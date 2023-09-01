# mcscript-ncci installation #
Prerequisites: `mcscript`, `shell`, `am`, `mfdnres`

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

  Set up the package in your `PYTHONPATH` by running `pip`:

  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  % python3 -m pip install --user --editable .
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  Note that the `.` here means to install the Python package defined by the code
  in the current directory.

  This will ***fail*** if you have not already installed `mcscript`. If this
  happens, go back and ensure that `mcscript` has been installed successfully.

  a. Subsequently updating source

  ~~~~~~~~~~~~~~~~
  % git pull
  % python3 -m pip install --user --editable .
  ~~~~~~~~~~~~~~~~

  This subsequent `pip install`, when updating the source code, is a precaution
  in case, e.g., the package dependencies have changed.

# 2. Environment Configuration

  The environment variable `NCCI_DATA_DIR_H2` is used to tell `mcscript-ncci`
  where to find interaction TBME files.  The scripting will search for TBME
  files in the directory given by `NCCI_DATA_DIR_H2`.  This may be given as a
  colon-separated list of directories to search.  That is, TBME files are
  expected to live in subdirectories of this directory, following this naming
  convention:

  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  <subdirectory_name>/<interaction_name>-<ob|tb>-<N1bmax|N2bmax>-<hw>.bin
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  e.g., ```run0164-JISP16-tb-20/JISP16-tb-20-20.bin```.

  #### @NDCRC: ####
  `.cshrc` or `.tcshrc`:
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # mcscript-ncci
  setenv GROUP_HOME "/afs/crc.nd.edu/group/nuclthy"
  setenv NCCI_DATA_DIR_H2 "${GROUP_HOME}/data/h2:${HOME}/code/mcscript-ncci/docs/examples"
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  `.bashrc` or `.bash_profile`:
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # mcscript-ncci
  export GROUP_HOME="/afs/crc.nd.edu/group/nuclthy"
  export NCCI_DATA_DIR_H2="${GROUP_HOME}/data/h2:${HOME}/code/mcscript-ncci/docs/examples"
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  #### @NERSC: ####
  `.cshrc` or `.tcshrc`:
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # mcscript-ncci
  # Use read-only mount point for /global/cfs/cdirs/m2032.
  # See https://docs.nersc.gov/performance/io/dvs/.
  setenv GROUP_HOME "/dvs_ro/cfs/cdirs/m2032"
  setenv NCCI_DATA_DIR_H2 "${GROUP_HOME}/data/h2:${HOME}/code/mcscript-ncci/docs/examples"
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  `.bashrc` or `.bash_profile`:
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # mcscript-ncci
  # Use read-only mount point for /global/cfs/cdirs/m2032.
  # See https://docs.nersc.gov/performance/io/dvs/.
  export GROUP_HOME="/dvs_ro/cfs/cdirs/m2032"
  export NCCI_DATA_DIR_H2="${GROUP_HOME}/data/h2:${HOME}/code/mcscript-ncci/docs/examples"
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  There are in fact several such environment variables indicating directories in
  which the scripting should search for various types of data file:

  * `NCCI_DATA_DIR_H2` for two-body matrix element files

  * `NCCI_DATA_DIR_REL` for relative matrix element files

  * `NCCI_DATA_DIR_DECOMPOSITION` for decomposition operators coefficient files

  But only `NCCI_DATA_DIR_H2` need be set for ordinary MFDn diagonalization runs.

  If you use `mcscript-ncci` to postprocess wave functions, you will also need
  to set the environment variable `NCCI_LIBRARY_PATH`, to tell `mcscript-ncci`
  where to find the results of prior runs (that is, the results, wave function,
  and task data files).  This may be given as a colon-separated list of
  directories to search.  For example, if your current runs are in
  `${SCRATCH}/runs`, runs retrieved from tape are in `${SCRATCH}/library`, and
  the example runs are in `${HOME}/code/mcscript-ncci/docs/examples`, you might
  define the following search path:

  `.cshrc` or `.tcshrc`:
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  setenv NCCI_LIBRARY_PATH "${SCRATCH}/runs:${SCRATCH}/library:${HOME}/code/mcscript-ncci/docs/examples"
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  `.bashrc` or `.bash_profile`:
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  export NCCI_LIBRARY_PATH="${SCRATCH}/runs:${SCRATCH}/library:${HOME}/code/mcscript-ncci/docs/examples"
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
