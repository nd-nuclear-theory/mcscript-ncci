
[MFDn]
Version = 15
Revision = v15b01-110-gf24e8ef-dirty
Platform = 
Username = 
ndiags   =        1
MPIranks  =        1
OMPthreads =        8

[PARAMETERS]

[Basis]
Nprotons  =        4
Nneutrons =        5
# Orbitals read in from file
TwoMj  =        1
parity =        1
WTmax  =     0.0000

[Diagonalization]
neivals   =        8
maxits    =      600
startit   =        0
selectpiv =        3
tol       =     0.0000

[Many-body matrix]
dimension  =              44133
numnonzero =            5117260

[Interaction]
# reading complete TBMEs in H2 format
Hrank  =        2
TBMEfile = tbme-H.bin

[Observables]
numTBops   =        2
# TBME file for relative R2 operator
TBMEfile(1) = tbme-rrel2.bin

# TBME files for additional operators
TBMEfile(2) = tbme-H.bin


[RESULTS]
# following Condon-Shortley phase conventions
# for conventions of reduced matrix elements and
# for Wigner-Eckart theorem, see Suhonen (2.27)

[Energies]
# Seq       J    n      T        Eabs        Eexc        Error    J-full
    1      2.5   1   0.500      -94.389      0.000     0.11E-04    2.5000
    2      0.5   1   0.500      -93.646      0.743     0.10E-04    0.5000
    3      1.5   1   0.500      -93.189      1.200     0.11E-04    1.5000
    4      3.5   1   0.500      -92.659      1.730     0.10E-04    3.5000
    5      2.5   2   0.500      -92.295      2.095     0.11E-04    2.5000
    6      0.5   2   0.500      -91.870      2.519     0.11E-04    0.5000
    7      1.5   2   0.500      -91.481      2.909     0.10E-04    1.5000
    8      3.5   2   0.500      -91.409      2.980     0.10E-04    3.5000

[Oscillator quanta]
# Seq    J    n      T      Amp(N)^2 
    1   2.5   1   0.500       1.000    
    2   0.5   1   0.500       1.000    
    3   1.5   1   0.500       1.000    
    4   3.5   1   0.500       1.000    
    5   2.5   2   0.500       1.000    
    6   0.5   2   0.500       1.000    
    7   1.5   2   0.500       1.000    
    8   3.5   2   0.500       1.000    

[M1 moments]
# M1 moments only calculated for runs with obdme enabled

[E2 moments]
# E2 moments only calculated for runs with obdme enabled

[Angular momenta]
# Seq    J    n      T      <L^2>      <S^2>      <Lp^2>     <Sp^2>     <Ln^2>     <Sn^2>        <J^2>
    1   2.5   1   0.500     7.7939     1.8392   -12.8125     0.6269   -13.8656     1.2385       8.7500
    2   0.5   1   0.500     1.9515     1.6840   -12.3876     0.6993   -14.5284     1.0053       0.7500
    3   1.5   1   0.500     5.7431     1.6116   -11.5028     0.7516   -14.3790     0.8777       3.7500
    4   3.5   1   0.500    13.9665     1.8840    -9.6222     0.6586   -12.4858     1.2324      15.7500
    5   2.5   2   0.500     8.1130     1.7474   -10.3272     0.6776   -11.9063     1.0511       8.7500
    6   0.5   2   0.500     1.8640     1.6824   -12.6582     0.6463   -16.7060     0.9986       0.7500
    7   1.5   2   0.500     6.1070     1.5826   -11.5077     0.5965   -13.7289     1.0195       3.7500
    8   3.5   2   0.500    16.8528     1.6063    -9.9618     0.7501   -10.6175     0.8630      15.7500

[Relative radii]
# Seq    J    n      T      r(p)       r(n)    r(matter)     r_pp       r_nn       r_pn
    1   2.5   1   0.500     0.0000     0.0000     0.0000     0.0000     0.0000     0.0000
    2   0.5   1   0.500     0.0000     0.0000     0.0000     0.0000     0.0000     0.0000
    3   1.5   1   0.500     0.0000     0.0000     0.0000     0.0000     0.0000     0.0000
    4   3.5   1   0.500     0.0000     0.0000     0.0000     0.0000     0.0000     0.0000
    5   2.5   2   0.500     0.0000     0.0000     0.0000     0.0000     0.0000     0.0000
    6   0.5   2   0.500     0.0000     0.0000     0.0000     0.0000     0.0000     0.0000
    7   1.5   2   0.500     0.0000     0.0000     0.0000     0.0000     0.0000     0.0000
    8   3.5   2   0.500     0.0000     0.0000     0.0000     0.0000     0.0000     0.0000

[Other 2-body observables]
# Seq    J    n      T     see header for TBME file names of observables
    1   2.5   1   0.500     -94.3892    
    2   0.5   1   0.500     -93.6465    
    3   1.5   1   0.500     -93.1888    
    4   3.5   1   0.500     -92.6589    
    5   2.5   2   0.500     -92.2947    
    6   0.5   2   0.500     -91.8705    
    7   1.5   2   0.500     -91.4806    
    8   3.5   2   0.500     -91.4095    

[Occupation probabilities]
# orb      n_rad   l   2*j
    1   pro    0    2    3    0.5152       0.4700       0.4419       0.4775       0.4697       0.5681       0.5144       0.4519    
    2   pro    0    2    5     3.099        3.064        3.067        3.007        2.977        3.051        2.972        3.067    
    3   pro    1    0    1    0.3858       0.4657       0.4913       0.5155       0.5532       0.3814       0.5138       0.4806    
# sum of proton occ.prob.     4.000        4.000        4.000        4.000        4.000        4.000        4.000        4.000    

    1   neu    0    2    3    0.5069       0.6456       0.8773       0.5145       0.6144        1.133       0.8738       0.9564    
    2   neu    0    2    5     4.074        3.406        3.469        3.967        3.288        3.324        3.328        3.495    
    3   neu    1    0    1    0.4188       0.9487       0.6538       0.5186        1.098       0.5423       0.7979       0.5490    
# sum of neutron occ.prob.    5.000        5.000        5.000        5.000        5.000        5.000        5.000        5.000    

