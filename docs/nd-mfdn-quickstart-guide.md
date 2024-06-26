ND MFDn workflow quickstart guide

Some initial pointers on where to look to get started.

04/17/23 (mac): Created (with slv, zz, ...).
06/16/23 (mac): Add mfdn-postprocessor installation instructions.

----------------

# ndconfig #

  This repository provides "configuration" makefiles which are needed to compile
  some of our codes under specific compilers and on specific computing systems
  (e.g., at NERSC).  It also provides "environment" files, which you should
  "source" into csh or bash, to set environment variables appropriate to a given
  computing environment (e.g., NERSC).  So this repository should be set up
  before any of the codes get compiled.
  
  - Cloning.  Clone the `ndconfig` repository.

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    % git clone https://github.com/nd-nuclear-theory/ndconfig.git
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  - Instructions.  See `INSTALL.md` for instructions.  For now, only consider
    the instructions in section 0 "Setting up `ndconfig`", which instructs you
    to set the `NDCONFIG_DIR` environment variable in your shell initialization
    file.  (The remainder of the instructions cover building codes that use
    `ndconfig`, such as `shell`, which we will tackle below.)

# shell #

   The `shell` package, written in C++, provides a suite of tools for generating
   matrix elements, as input to `mfdn` or `mfdn-transitions`.

  - Cloning and building.  Follow the directions given in the `INSTALL.md` file
    for `ndconfig`, now looking at Sections 1-4.  Be sure to follow all the
    steps through `make install`.  At the end of this, you should have
    executable files installed under your intended installation directory, e.g.,
    if you are at NERSC, and if you follow the directory structure described in
    the example, your executable files will be in

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ${HOME}/code/install/$(CRAY_CPU_TARGET)/shell/bin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  - Code test.  Try out the "Optional sanity check for `shell` project" given in
    Section 5 of the `INSTALL.md` file for `ndconfig`.

# mfdn #

  - Cloning.  You can clone from either the ISU original repository

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    % git clone https://github.com/isu-nuclear-theory/mfdn.git
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    or from ND's fork

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    % git clone https://github.com/nd-nuclear-theory/mfdn.git
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    These are both private repositories, and require read permission to be
    granted by ISU or ND, respectively.

  - Instructions.  See `README.md` for installation instructions.  Important
    topics include:

    + Setting up a symlink to the appropriate config file.  (These are local to
      mfdn's repository, not our standard ndconfig config.mk files.)  For example:

      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
       % ln -s config/config_Perlmutter_CPU_gnu.mk config.mk
      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    + Recommendations on modules to load.  For instance, on Cori at one point,
    better performance was obtained by unloading the default cray-libsci module,
    to ensure that the MKL linear algebra libraries were used instead.

    + Different compilation modes to select for (a) the interaction file format
      and (b) the eigensolver.

  - Environment.  You can source our usual "env" file from ndconfig, for
    whichever system and compiler you are targeting.  But beware that the
    recommendations in `README.md` might augment or supersede these, e.g., `module
    unload cray-libsci`.

  - Building.  First run 'make' with no arguments to display help.  Note that
    you will have to specify which TBME file format to use (`VAR=...`) and which
    solver to use (`SOLVER=...`), unless you want the default choices.  A typical
    invocation is thus:

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    % make mfdn SOLVER=lan
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  - Installing executable.  Below, when you start using the scripting in
    `mcscript-ncci`, that scripting will look for the executable in your a
    directory specified by various environment variables.  So we have to give a
    little preview of this now...  For this to work, you need to manually copy
    the executable to this expected location.  This is controlled by the
    `MCSCRIPT_INSTALL_HOME` environment variable (and, at NERSC, the
    CRAY_CPU_TARGET environment variable).  For instance, suppose
    `MCSCRIPT_INSTALL_HOME` is set to `${HOME}/code/install`.  If you are on
    your own own workstation (or a non-Cray environment), then you should copy
    the exectuble as illustrated here:
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    % mkdir --parents ~/code/install/mfdn/bin
    % cp xmfdn-h2-lan ~/code/install/mfdn/bin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Or, equivalently, if you like incantations involving environment variables:
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    % mkdir --parents ${MCSCRIPT_INSTALL_HOME}/mfdn/bin
    % cp xmfdn-h2-lan ${MCSCRIPT_INSTALL_HOME}/mfdn/bin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    If you are at NERSC, on perlmutter, and compiling for CPUs, then the
    environment variable `CRAY_CPU_TARGET` is set to `x86-milan`.  In this case,
    you should copy the exectuble as illustrated here:

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    % mkdir --parents ~/code/install/x86-milan/mfdn/bin
    % cp xmfdn-h2-lan ~/code/install/x86-milan/mfdn/bin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Or, equivalently, if you like incantations involving environment variables:
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    % mkdir --parents ${MCSCRIPT_INSTALL_HOME}/${CRAY_CPU_TARGET}/mfdn/bin
    % cp xmfdn-h2-lan ${MCSCRIPT_INSTALL_HOME}/${CRAY_CPU_TARGET}/mfdn/bin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Note that the executable filename will need to match the executable filename
    in the task dictionary in your run script, e.g., in the example
    `runmfdn13.py` which you will try out below, the executable is specified as:

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
       "mfdn_executable": "xmfdn-h2-lan"
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Hint: If you need to work with various versions of the mfdn executable,
    e.g., if you are switching between running versions compiled with different
    compilers, or built from different commits of mfdn, then you may want to use
    a subdirectory structure to keep track of different executables, e.g.,

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
       "mfdn_executable": "f94feb3/xmfdn-h2-lan"
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# mfdn-transitions

  - Cloning.  You can clone from either the ND original repository

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    % git clone https://github.com/nd-nuclear-theory/mfdn-transitions.git
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    or from ISU's fork (this might now be quite the latest version)

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    % git clone https://github.com/isu-nuclear-theory/mfdn-transitions.git
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    These are both private repositories, and require read permission to be
    granted by ND or ISU, respectively.

  - Environment.  You can source our usual "env" file from ndconfig, for
    whichever system and compiler you are targeting.

  - Building.  This code is built using CMake.  See instructions in `INSTALL.md`.
  
  - Installing executable.  See instructions in `INSTALL.md` for running `cmake`
    with the `--install` option.  Or else, you can manually copy `xtransitions`
    to the appropriate directory, much as described above for `mfdn`.  For
    instance, on your own workstation (or a non-Cray environment):
  
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    % mkdir --parents ${MCSCRIPT_INSTALL_HOME}/mfdn-transitions/bin
    % cp xtransitions ${MCSCRIPT_INSTALL_HOME}/mfdn-transitions/bin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Or, at NERSC, on perlmutter CPU:

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    % mkdir --parents ${MCSCRIPT_INSTALL_HOME}/${CRAY_CPU_TARGET}/mfdn-transitions/bin
    % cp xtransitions ${MCSCRIPT_INSTALL_HOME}/${CRAY_CPU_TARGET}/mfdn-transitions/bin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  
# mcscript #

  This package provides basic scripting tools for workflow management.  There is
  nothing specific to NCCI applications, but our NCCI scripting below depends on
  this package, so it is a good starting place for getting your hands dirty.

  - Cloning.  Clone the `mcscript-ncci` repository.

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    % git clone https://github.com/nd-nuclear-theory/mcscript.git
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      
  - Instructions.  See `INSTALL.md` for instructions.

  - See "qsubm --help" for the workings of qsubm.

    + qsubm: (1) sets the environment variables that our script expects, (2)
      sets up a run directory for the script to execute in, (3) submits the
      batch job to the queue

  - Run the examples described in INSTALL.md, to get the basic idea of a
    task-based run.

# mcscript-ncci #

  This package provides scripting (for use with mcscript) specific to NCCI runs,
  with shell/mfdn/mfdn-transitions and possibly other tools.

  - Dependencies: mcscript, am, mfdnres.  STOP!  You have presumably already
    installed mcscript (as described above).  Now take a moment to install am
    and mfdnres.  Clone the `am` and `mfdnres` repositories:

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    % git clone https://github.com/nd-nuclear-theory/am.git
    % git clone https://github.com/nd-nuclear-theory/mfdnres.git
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Then see their `INSTALL.md` files for further instructions!

  - Cloning.  Clone the `mcscript-ncci` repository.

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    % git clone https://github.com/nd-nuclear-theory/mcscript-ncci.git
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      
  - Instructions.  See `INSTALL.md` for instructions.
  
  - Examples.  This package comes with some example run scripts, under
    `docs/examples`.  Follow the instructions in `docs/examples/README.md`.

  - The examples which come with `mcscript-ncci` are pretty minimal.  For
    instance, they don't know about the locations where we keep our group
    interaction files and our partition files.  For actual recent examples of
    production runs, look in our `runs` repository, e.g.,
    `mcaprio/runmac0718.py`.

  - The examples also don't go into machine specific information on the
    parameters for running properly in a parallel environment (ranks, threads,
    ...) or on the proper queues to use.  For information on machines and queues at NERSC, see:

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    https://docs.nersc.gov/systems/
    https://docs.nersc.gov/jobs/policy/
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    For information on machine-specific parameters for running at NERSC, see
    `notes/nersc-run-parameters.txt` in our group `runs` repository.

