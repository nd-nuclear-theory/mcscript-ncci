
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
Nprotons  =        0
Nneutrons =        2
# Orbitals read in from file
TwoMj  =        0
parity =        1
WTmax  =     0.0000

[Diagonalization]
neivals   =        8
maxits    =      600
startit   =        0
selectpiv =        3
tol       =     0.0000

[Many-body matrix]
dimension  =                 14
numnonzero =                101

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
    1      0.0   1   1.000      -11.932      0.000     0.11E-05    0.0000
    2      2.0   1   1.000       -9.933      1.998     0.68E-06    2.0000
    3      4.0   1   1.000       -8.405      3.527     0.38E-06    4.0000
    4      2.0   2   1.000       -7.572      4.360     0.50E-06    2.0000
    5      0.0   2   1.000       -7.339      4.593     0.67E-06    0.0000
    6      3.0   1   1.000       -6.505      5.426     0.57E-06    3.0000
    7      4.0   2   1.000       -2.912      9.019     0.62E-06    4.0000
    8      2.0   3   1.000       -2.051      9.881     0.30E-06    2.0000

[Oscillator quanta]
# Seq    J    n      T      Amp(N)^2 
    1   0.0   1   1.000       1.000    
    2   2.0   1   1.000       1.000    
    3   4.0   1   1.000       1.000    
    4   2.0   2   1.000       1.000    
    5   0.0   2   1.000       1.000    
    6   3.0   1   1.000       1.000    
    7   4.0   2   1.000       1.000    
    8   2.0   3   1.000       1.000    

[M1 moments]
# M1 moments only calculated for runs with obdme enabled

[E2 moments]
# E2 moments only calculated for runs with obdme enabled

[Angular momenta]
# Seq    J    n      T      <L^2>      <S^2>      <Lp^2>     <Sp^2>     <Ln^2>     <Sn^2>        <J^2>
    1   0.0   1   1.000     0.2974     0.2974     0.0000     0.0000    -8.1044     0.2974       0.0000
    2   2.0   1   1.000     5.3206     0.5734     0.0000     0.0000    -2.8799     0.5734       6.0000
    3   4.0   1   1.000    15.4582     1.1355     0.0000     0.0000     4.9582     1.1355      20.0000
    4   2.0   2   1.000     5.3818     0.7087     0.0000     0.0000    -1.3941     0.7087       6.0000
    5   0.0   2   1.000     0.1105     0.1105     0.0000     0.0000    -0.5282     0.1105       0.0000
    6   3.0   1   1.000     6.0608     2.0000     0.0000     0.0000     1.5000     2.0000      12.0000
    7   4.0   2   1.000    16.5418     0.8645     0.0000     0.0000     6.0418     0.8645      20.0000
    8   2.0   3   1.000     4.8247     1.5520     0.0000     0.0000    -5.2657     1.5520       6.0000

[Relative radii]
# Seq    J    n      T      r(p)       r(n)    r(matter)     r_pp       r_nn       r_pn
    1   0.0   1   1.000        NaN     0.0000     0.0000     0.0000     0.0000     0.0000
    2   2.0   1   1.000        NaN     0.0000     0.0000     0.0000     0.0000     0.0000
    3   4.0   1   1.000        NaN     0.0000     0.0000     0.0000     0.0000     0.0000
    4   2.0   2   1.000        NaN     0.0000     0.0000     0.0000     0.0000     0.0000
    5   0.0   2   1.000        NaN     0.0000     0.0000     0.0000     0.0000     0.0000
    6   3.0   1   1.000        NaN     0.0000     0.0000     0.0000     0.0000     0.0000
    7   4.0   2   1.000        NaN     0.0000     0.0000     0.0000     0.0000     0.0000
    8   2.0   3   1.000        NaN     0.0000     0.0000     0.0000     0.0000     0.0000

[Other 2-body observables]
# Seq    J    n      T     see header for TBME file names of observables
    1   0.0   1   1.000     -11.9318    
    2   2.0   1   1.000     -9.93335    
    3   4.0   1   1.000     -8.40459    
    4   2.0   2   1.000     -7.57171    
    5   0.0   2   1.000     -7.33926    
    6   3.0   1   1.000     -6.50542    
    7   4.0   2   1.000     -2.91241    
    8   2.0   3   1.000     -2.05051    

[Occupation probabilities]
# orb      n_rad   l   2*j
    1   pro    0    2    3     0.000        0.000        0.000        0.000        0.000        0.000        0.000        0.000    
    2   pro    0    2    5     0.000        0.000        0.000        0.000        0.000        0.000        0.000        0.000    
    3   pro    1    0    1     0.000        0.000        0.000        0.000        0.000        0.000        0.000        0.000    
# sum of proton occ.prob.     0.000        0.000        0.000        0.000        0.000        0.000        0.000        0.000    

    1   neu    0    2    3    0.9812E-01   0.5801E-01   0.6305E-01   0.1672E-01   0.3156E-02   0.1014E-01   0.9369       0.9902    
    2   neu    0    2    5     1.552        1.559        1.937        1.363       0.3533        1.000        1.063       0.9415    
    3   neu    1    0    1    0.3497       0.3832       0.3155E-12   0.6207        1.644       0.9899       0.3669E-14   0.6827E-01
# sum of neutron occ.prob.    2.000        2.000        2.000        2.000        2.000        2.000        2.000        2.000    

