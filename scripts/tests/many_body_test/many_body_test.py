from imports import *
from nhqm.bases import many_body as mb
from nhqm.bases import naive_many_mody as nmb
from scipy.sparse import lil_matrix
import scipy as sp
from scipy import linalg
from plotting import *
from nhqm.bases import mom_space as mom
from nhqm.problems import He5
from nhqm.calculations import QM as calc


problem = He5.problem   
order = 1*3
l = 0
j = 0.5
problem.V0 = -47.
peak_x = 0.17
peak_y = 0.07
k_max = 2.5
num_states = 10
num_particles = 2

contour = calc.triangle_contour(peak_x, peak_y, k_max, order/3)
points, _ = contour

args = (problem, l, j)
H = calc.contour_hamiltonian(mom.H_element_contour, contour, args)
eigvals, eigvecs = calc.energies(H)

eigvecs, _ = linalg.eig(H)
states = mb.gen_states(order, num_particles)
mb_H = mb.hamiltonian(states, H, eigvecs)


###

naivecomb = nmb.get_naive_combinations(num_states, num_particles)
comb = mb.get_combinations(num_states, num_particles)

#print naivecomb
print len(naivecomb) - len(comb)

for i in xrange( min ( len(naivecomb), len(comb) ) ):
    if naivecomb[i] != comb[i]:
        print naivecomb[i], comb[i]






