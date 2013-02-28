from __future__ import division
import scipy as sp
from scipy import linalg, integrate

def hamiltonian(element_function, args=None, 
                order=20, hermitian=False):
    """Given an element_function(n, n_prim) calculates energies."""
    H = sp.empty((order, order), complex)
    for n in xrange(order):
        limit = (n + 1) if hermitian else order
        for n_prim in xrange(limit):
            H[n, n_prim] = element_function(n, n_prim, *args)
            if hermitian:
                H[n_prim, n] = H[n, n_prim]
    return H

def contour_hamiltonian(element_function, contour, args=None):
    if contour[0] == 0:
        contour = contour[1:]
    order = len(contour)
    H = sp.empty((order, order), complex)
    
    steps = calculate_steps(contour)
    
    for (n, k) in enumerate(contour):
        for (n_prim, k_prim) in enumerate(contour):
            H[n, n_prim] = element_function(k, k_prim, 
                                            steps[n_prim], *args)
    return H

def calculate_steps(contour):
    shifted = sp.roll(contour, 1)
    shifted[0] = 0
    return contour - shifted

def energies(H, hermitian=False):
    """Given a hamiltonian matrix, calculates energies and sorts them."""
    if hermitian:
        eigvals, eigvecs = linalg.eigh(H)
    else:
        eigvals, eigvecs = linalg.eig(H)
        indexes = eigvals.argsort()
        eigvals = sp.real_if_close(eigvals[indexes])
        eigvecs = eigvecs[:, indexes]
    return eigvals, eigvecs

def gen_wavefunction(eigvec, basis_function, contour=None):
    length = len(eigvec)
    if contour == None:
        @sp.vectorize
        def wavefunction(r):
            result = sp.empty(length, complex)
            for (n, weight) in enumerate(eigvec):
                result[n] = weight * basis_function(r, n)
            return sp.sum(result)
    else:
        steps = calculate_steps(contour)
        @sp.vectorize
        def wavefunction(r):
            result = sp.empty(length, complex)
            for (n, weight) in enumerate(eigvec):
                k = contour[n]
                step = steps[n]
                result[n] = weight * basis_function(r, k, step)
            return sp.sum(result)
    return wavefunction

def absq(x):
    return sp.real(x * sp.conj(x))

def norm(f, start, stop, weight = lambda x: 1):
    def integrand(x):
        return absq(f(x)) * weight(x);
    (N, _) = sp.integrate.quad(integrand, start, stop)
    return N


def normalize(f, start, stop, weight = lambda x: 1):
    N = norm(f, start, stop, weight = weight)
    return lambda x: f(x) / sp.sqrt(N)
    
#
# Tests
#
   
import unittest
   
class SinTests(unittest.TestCase):
    
    def setUp(self):
        self.a = 0
        self.b = 5
        self.f = lambda x: sp.sin(sp.pi / self.b * x)
    
    def testNorm(self):
        N = norm(self.f, self.a, self.b)
        self.assertEquals(N, (self.b - self.a) * .5 )
    
    def testNormalize(self):
        g = normalize(self.f, self.a, self.b)
        N = norm(g, self.a, self.b)
        self.assertEquals(N, 1.0)
        
class ComplexTests(unittest.TestCase):
    pass
    
class WeightTests(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()
    