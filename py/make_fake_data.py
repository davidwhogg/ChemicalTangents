"""
This file is part of the Chemical Tangents project
Copyright 2018 David W. Hogg (NYU)

to-do
-----
- write code
- test code
"""

import numpy as np
from chemical_tangents import *

def make_one_fake_star(pars):
    """
    bugs:
    -----
    - not written
    - not adding noise to anything
    """
    # unpack pars
    foo, a, b, c, acceleration, sunpars, dynpars = pars
    # choose x,y
    x, y = np.random.uniform(-1000. * pc, 1000. * pc, size=2) # pc
    # choose Ez isothermally
    lnEz = foo + np.log(np.random.normal() ** 2)
    # choose metallicity by a polynomial
    abundnace = a + b * lnEz + c * lnEz * lnEz + 0.25 * np.random.normal()
    # choose an angle
    phi_z = 2. * np.pi * np.random.uniform()
    # integrate
    v0 = np.sqrt(2. * np.exp(lnEz)) * km / s # woot
    z, vz = integrate_to_phi(phi_z, v0, 0.1 * Myr, acceleration, dynpars)
    return x, y, z - sunpars[0], vz - sunpars[1]

def selection_function(x, y, z):
    """
    evaluate selection function at a point.

    bugs:
    -----
    - need to make sky cut work!
    """
    # not far away
    if x * x + y * y + z * z > (1000. * pc) ** 2:
        return 0.
    # not in the Galactic plane
    if z * z / (x * x + y * y) < np.tan(20. * np.pi / 180.) ** 2:
        return 0.
    # not way North
#    if x * xhat + y * yhat + z * zhat > something:
#        return 0.
    return 1.

def make_catalog(N, pars):
    n = 0
    poss, vzs = np.zeros((N, 3)), np.zeros(N)
    while n < N:
        r = np.random.uniform()
        x, y, z, vz = make_one_fake_star(pars)
        if r < selection_function(x, y, z):
            poss[n, :] = x, y, z
            vzs[n] = vz
            n += 1
    return poss, vzs

def write_catalog():
    whatever
    return None

if __name__ == "__main__":

    pars = (5., 0., -0.5, -0.1, sech_squared_acceleration, [10. * pc, 1. * (km / s)], [65. * sigunits, 350. * pc])
    poss, vzs = make_catalog(16, pars)
    print(poss[:, 2] / pc, vzs / (km / s))
