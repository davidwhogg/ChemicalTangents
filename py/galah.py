"""
This file is part of the ChemicalTangents project.
Copyright 2018 David W. Hogg (MPIA).

bugs:
-----
- I don't know what parameters Pyia is using to go to Galactic 6-space.
"""

from astropy.table import Table
import astropy.coordinates as coord
import astropy.units as u
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from pyia import GaiaData
from integrate_orbits import *

def plot_some_abundances(galah, galcen):
    nx, ny = 3, 2
    fig, ax = plt.subplots(ny, nx, figsize=(nx * 5, ny * 5), sharex=True, sharey=True)
    ax = ax.flatten()
    for i,aname in enumerate(abundancenames):
        abundance = getattr(galah, aname)
        good = np.abs(abundance) < 5.
        vmin, vmax = np.percentile(abundance[good], [5., 95.])
        foo = ax[i].scatter(galcen[good].v_z.to(u.km/u.s).value, 
                         galcen[good].z.to(u.pc).value,
                         marker=".", s=3000/np.sqrt(np.sum(good)),
                         c=abundance[good], vmin=vmin, vmax=vmax, alpha=0.3,
                         cmap=mpl.cm.plasma, rasterized=True)
        ax[i].text(-vzmax * 0.96, zmax * 0.96, abundancelabels[aname], ha="left", va="top", backgroundcolor="w")
        if i % nx == 0:
            ax[i].set_ylabel("$z$ [pc]")
        if i // nx + 1 == ny:
            ax[i].set_xlabel("$v_z$ [km/s]")
    ax[0].set_xlim(-vzmax, vzmax)
    ax[0].set_ylim(-zmax, zmax)
    return fig.tight_layout()

if __name__ == "__main__":

    # read data and cut
    galah = GaiaData('../data/GALAH-GaiaDR2-xmatch.fits.gz')
    galah = galah[np.isfinite(galah.parallax_error)]
    galah = galah[(galah.parallax / galah.parallax_error) > 10.]
    galah = galah[np.isfinite(galah.teff) & (galah.teff > 4000*u.K) & (galah.teff < 6500*u.K)]
    galah = galah[np.isfinite(galah.logg) & (galah.logg < 3.5)]

    # make coordinates
    c = galah.get_skycoord(radial_velocity=galah.rv_synt)
    galcen = c.transform_to(coord.Galactocentric(z_sun=0*u.pc))
    zs = galcen.z.to(u.pc).value
    vs = galcen.v_z.to(u.km/u.s).value

    # trim on coordinates
    zlim = 1500. # pc
    vlim =   75. # km / s
    inbox = (np.abs(zs) < zlim) & (np.abs(vs) < vlim)
    galah = galah[inbox]
    galcen = galcen[inbox]

    # get actions and angles
    sigunits = 1. * M_sun / (pc ** 2)
    pars = np.array([-10. * pc, 50. * sigunits, 300 * pc])
    zs = galcen.z.to(u.pc).value
    vs = galcen.v_z.to(u.km/u.s).value
    vmaxs, phis = paint_actions_angles(zs, vs, pars)

    # plot
    nx, ny = 2, 1
    fig, ax = plt.subplots(ny, nx, figsize=(nx * 5, ny * 5), sharex=True, sharey=True)
    ax = ax.flatten()
    for i, q in enumerate([vmaxs, phis]):
        vmin, vmax = np.percentile(q, [0.1, 99.9])
        foo = ax[i].scatter(vs, zs,
                         marker=".", s=3000/np.sqrt(len(vs)),
                         c=q, vmin=vmin, vmax=vmax, alpha=0.3,
                         cmap=mpl.cm.plasma, rasterized=True)
        if i % nx == 0:
            ax[i].set_ylabel("$z$ [pc]")
        if i // nx + 1 == ny:
            ax[i].set_xlabel("$v_z$ [km/s]")
    ax[0].set_xlim(-vlim, vlim)
    ax[0].set_ylim(-zlim, zlim)
    fig.savefig("galah_action_angle.pdf")

    # plot angle plots
    nx, ny = 1, 8
    fig, ax = plt.subplots(ny, nx, figsize=(10, 10), sharex=True, sharey=True)
    q = vmaxs
    vmin, vmax = np.percentile(q, [0.5, 99.5])
    for i in range(ny):
        vmaxlims = np.percentile(vmaxs, [100 * i / ny, 100 * (i + 1) / ny])
        inside = (vmaxs > vmaxlims[0]) * (vmaxs < vmaxlims[1])
        print(phis[inside].shape, galah[inside].mg_fe.shape, q.shape)
        foo = ax[i].scatter(phis[inside], galah[inside].mg_fe,
                            marker=".", s=1000/np.sqrt(np.sum(inside)),
                            c=q[inside], vmin=vmin, vmax=vmax, alpha=0.3,
                            cmap=mpl.cm.plasma, rasterized=True)
        if i % nx == 0:
            ax[-1].set_ylabel("[Mg/Fe] [dex]")
        if i // nx + 1 == ny:
            ax[-1].set_xlabel(r"conjugate angle $\theta_z$ [rad]")
    ax[-1].set_xlim(3.4, 4.)
    ax[-1].set_ylim(-0.3, 0.6)
    fig.savefig("galah_mg_angle.pdf")

if False:

    # decide what and how to plot
    abundancenames = ["fe_h", "mg_fe", "o_fe", "al_fe", "mn_fe", "eu_fe"]
    abundancelabels = {}
    abundancelabels["fe_h"] = "[Fe/H]"
    abundancelabels["mg_fe"] = "[Mg/Fe]"
    abundancelabels["o_fe"] = "[O/Fe]"
    abundancelabels["al_fe"] = "[Al/Fe]"
    abundancelabels["mn_fe"] = "[Mn/Fe]"
    abundancelabels["eu_fe"] = "[Eu/Fe]"
    zmax = 1500. # pc
    vzmax = 75. # km / s

    # plot
    foo = plot_some_abundances(galah, galcen)
    plt.savefig("galah_full_sample.pdf")
