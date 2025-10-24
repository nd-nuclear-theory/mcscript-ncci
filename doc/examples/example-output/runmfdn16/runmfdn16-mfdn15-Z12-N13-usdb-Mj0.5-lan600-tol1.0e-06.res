
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
    1      2.5   1   0.500      -94.401      0.000     0.97E-05    2.5000
    2      0.5   1   0.500      -93.796      0.605     0.11E-04    0.5000
    3      1.5   1   0.500      -93.304      1.097     0.10E-04    1.5000
    4      3.5   1   0.500      -92.681      1.721     0.98E-05    3.5000
    5      2.5   2   0.500      -92.406      1.995     0.10E-04    2.5000
    6      0.5   2   0.500      -91.818      2.583     0.10E-04    0.5000
    7      1.5   2   0.500      -91.590      2.811     0.10E-04    1.5000
    8      3.5   2   0.500      -91.500      2.901     0.11E-04    3.5000

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
    1   2.5   1   0.500     7.8681     1.9429   -12.9237     0.6656   -13.8117     1.2877       8.7500
    2   0.5   1   0.500     1.9716     1.7907   -12.3140     0.7446   -14.4845     1.0431       0.7500
    3   1.5   1   0.500     5.8743     1.6842   -11.4872     0.7920   -14.1990     0.8988       3.7500
    4   3.5   1   0.500    13.9755     1.9996    -9.6961     0.7098   -12.5295     1.2798      15.7500
    5   2.5   2   0.500     8.0970     1.8652   -10.3025     0.7332   -11.9818     1.0940       8.7500
    6   0.5   2   0.500     1.9525     1.7158   -12.4178     0.6893   -16.6745     0.9999       0.7500
    7   1.5   2   0.500     6.1624     1.6619   -11.5044     0.6592   -13.7288     1.0359       3.7500
    8   3.5   2   0.500    17.0196     1.6595   -10.0027     0.7824   -10.4193     0.8818      15.7500

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
    1   2.5   1   0.500     -94.4013    
    2   0.5   1   0.500     -93.7959    
    3   1.5   1   0.500     -93.3040    
    4   3.5   1   0.500     -92.6807    
    5   2.5   2   0.500     -92.4058    
    6   0.5   2   0.500     -91.8182    
    7   1.5   2   0.500     -91.5901    
    8   3.5   2   0.500     -91.5000    

[Occupation probabilities]
# orb      n_rad   l   2*j
    1   pro    0    2    3    0.4695       0.4431       0.4152       0.4247       0.4301       0.5134       0.4639       0.4242    
    2   pro    0    2    5     3.161        3.106        3.111        3.076        3.030        3.082        3.025        3.115    
    3   pro    1    0    1    0.3693       0.4512       0.4739       0.4996       0.5400       0.4048       0.5113       0.4613    
# sum of proton occ.prob.     4.000        4.000        4.000        4.000        4.000        4.000        4.000        4.000    

    1   neu    0    2    3    0.4637       0.6012       0.8348       0.4719       0.5622        1.108       0.8548       0.9110    
    2   neu    0    2    5     4.124        3.456        3.515        4.014        3.344        3.366        3.372        3.540    
    3   neu    1    0    1    0.4122       0.9432       0.6506       0.5138        1.094       0.5260       0.7729       0.5487    
# sum of neutron occ.prob.    5.000        5.000        5.000        5.000        5.000        5.000        5.000        5.000    

