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
  % python3 -m pip install --user .
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  Note that the `.` here means to install the Python package defined by the code
  in the current directory.  Note also that `mcscript` and `mcscript.ncci` are
  not compatible with the `--editable` flag to `pip` (if you attempt an editable
  installation, you are likely to encounter errors such as `ModuleNotFoundError:
  No module named 'mcscript.ncci'`).

  This will ***fail*** if you have not already installed `mcscript`. If this
  happens, go back and ensure that `mcscript` has been installed successfully.

  a. Subsequently updating source

  ~~~~~~~~~~~~~~~~
  % git pull
  % python3 -m pip install --user .
  ~~~~~~~~~~~~~~~~

# 2. Environment Configuration

  The environment variable `NCCI_DATA_DIR_H2` is used to tell `mcscript-ncci`
  where to find interaction TBME files.  The scripting will search for TBME
  files in the directory (or a series of directories) given by
  `NCCI_DATA_DIR_H2`.  This may be given as a colon-separated list of
  directories to search, e.g., there might be one set of interaction files in a
  shared group project "data" directory, and another in your own private "data"
  directory.
  
  Then, TBME files are expected to live in subdirectories of this directory,
  e.g., typically all the interaction files for the same interaction (but at
  different hw, with different regulator or SRG parameter, etc.) might lie in
  the same subdirectory.  The files themselves are expected by the scripting
  (though this can be overriden if needed) to follow a standard naming
  convention:

  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  <interaction_name>-<ob|tb>-<N1bmax|N2bmax>-<hw>.bin
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  Thus, e.g., the group's library of interaction files may be in a shared
  directory ```/project/data/h2```.  This is where the environment variable
  `NCCI_DATA_DIR_H2` should point.  Then there might be subdirectories
  `daejeon16`, `jisp16`, etc., for different interactions.  These will be
  specified in your run script.  Then individual files might have names like
  ```run0164-JISP16-tb-20/JISP16-tb-20-20.bin```.

  There are in fact several such environment variables indicating directories in
  which the scripting should search for various types of data file:

    * `NCCI_DATA_DIR_H2` for two-body matrix element files

    * `NCCI_DATA_DIR_REL` for relative matrix element files

    * `NCCI_DATA_DIR_DECOMPOSITION` for decomposition operators coefficient files

  However, only `NCCI_DATA_DIR_H2` need be set for ordinary MFDn diagonalization runs.

  E.g., for running under project m2032 at NERSC:

  For `.cshrc` or `.tcshrc`:
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # mcscript-ncci
  # Use read-only mount point for /global/cfs/cdirs/m2032.
  # See https://docs.nersc.gov/performance/io/dvs/.
  setenv GROUP_HOME "/dvs_ro/cfs/cdirs/m2032"
  setenv NCCI_DATA_DIR_H2 "${GROUP_HOME}/data/h2:${HOME}/code/mcscript-ncci/docs/examples/example-data"
  setenv NCCI_DATA_DIR_DECOMPOSITION "${GROUP_HOME}/data/u3-subspaces/decomposition:${HOME}/code/mcscript-ncci/docs/examples/example-data"
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  For `.bashrc` or `.bash_profile`:
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # mcscript-ncci
  # Use read-only mount point for /global/cfs/cdirs/m2032.
  # See https://docs.nersc.gov/performance/io/dvs/.
  export GROUP_HOME="/dvs_ro/cfs/cdirs/m2032"
  export NCCI_DATA_DIR_H2="${GROUP_HOME}/data/h2:${HOME}/code/mcscript-ncci/docs/examples/example-data"
  export NCCI_DATA_DIR_DECOMPOSITION="${GROUP_HOME}/data/u3-subspaces/decomposition:${HOME}/code/mcscript-ncci/docs/examples/example-data"
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  Or, at the ND CRC, one would set `GROUP_HOME="/afs/crc.nd.edu/group/nuclthy"`
  and then proceed identically.  On your own laptop or workstation, you might
  substitute `GROUP_HOME=${HOME}`.
  
  If you use `mcscript-ncci` to postprocess wave functions, you will also need
  to set one more environment variable:
  
    * `NCCI_LIBRARY_PATH` for run directories containing wave functions
    
  This will tell `mcscript-ncci` where to find the results of prior runs (that
  is, the numerical results files, wave function files, and task data files).
  This may be given as a colon-separated list of directories to search.  For
  example, if your current runs are in `${SCRATCH}/runs`, runs retrieved from
  tape are in `${SCRATCH}/library`, and the example runs are in
  `${HOME}/code/mcscript-ncci/docs/examples`, you might define the following
  search path:

  For `.cshrc` or `.tcshrc`:
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  setenv NCCI_LIBRARY_PATH "${SCRATCH}/runs:${SCRATCH}/library:${HOME}/code/mcscript-ncci/docs/examples"
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  For `.bashrc` or `.bash_profile`:
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  export NCCI_LIBRARY_PATH="${SCRATCH}/runs:${SCRATCH}/library:${HOME}/code/mcscript-ncci/docs/examples"
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
