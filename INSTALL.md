# mcscript-ncci installation #
Prerequisites: `mcscript`, `shell`

# 1. Retrieving source

  Change to the directory where you want the repository to be installed,
  e.g.,
  ~~~~~~~~~~~~~~~~
  % cd ~/code
  ~~~~~~~~~~~~~~~~

  Clone the shell repository and all submodules.  In the following,
  replace "netid" with your ND NetID:
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  % git clone ssh://<netid>@crcfe01.crc.nd.edu/afs/crc.nd.edu/group/nuclthy/git/mcscript-ncci.git
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  Or, from the secondary (public) repository on github:
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  % git clone https://github.com/nd-nuclear-theory/mcscript-ncci.git
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  Setup the package in your `PYTHONPATH` by running `pip` (or `pip3` on Debian):
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  % pip install --user --editable mcscript-ncci/
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  This will ***fail*** if you have not already installed `mcscript`. If this
  happens, go back and ensure that `mcscript` has been installed successfully.

  Then change your working directory (cd) to the project directory for
  all the following steps.

  a. Subsequently updating source
  ~~~~~~~~~~~~~~~~
  % git pull
  ~~~~~~~~~~~~~~~~

# 2. Environment Configuration
  `mcscript-ncci` requires environment variables to find interaction files.

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
  setenv NCCI_DATA_DIR_H2 "/project/projectdirs/m2032/data/h2"
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  `.bashrc` or `.bash_profile`:
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # mcscript-ncci
  export NCCI_DATA_DIR_H2="/project/projectdirs/m2032/data/h2"
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
