# Installation
If you are using mcscript-ncci, you will want to set additional environment
variables in your .cshrc/.bashrc file.

### @NDCRC: ###
.cshrc:
~~~
# mcscript-ncci
setenv NCCI_DATA_DIR_H2 "/afs/crc.nd.edu/group/nuclthy/data/h2"
setenv PYTHONPATH ${HOME}/code/mcscript-ncci:${PYTHONPATH}
~~~

.bashrc or .bash_profile:
~~~
# mcscript-ncci
export NCCI_DATA_DIR_H2="/afs/crc.nd.edu/group/nuclthy/data/h2"
export PYTHONPATH="${HOME}/code/mcscript-ncci:${PYTHONPATH}"
~~~

### @NERSC: ###
.cshrc:
~~~
# mcscript-ncci
setenv NCCI_DATA_DIR_H2 "/project/projectdirs/m2032/data/h2"
setenv PYTHONPATH ${SHELL_PROJECT_DIR}/script:${PYTHONPATH}
~~~

.bashrc or .bash_profile:
~~~
# mcscript-ncci
export NCCI_DATA_DIR_H2="/project/projectdirs/m2032/data/h2"
export PYTHONPATH="${HOME}/code/mcscript-ncci:${PYTHONPATH}"
~~~
