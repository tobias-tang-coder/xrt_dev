# -*- coding: utf-8 -*-
u"""
This test script exemplifies two implementations of hyperbolic mirror:
HyperbolicMirrorParam and HyperboloidCapillaryMirror (pick out the wanted class
below). The former one can be open or closed (a complete surface of revolution)
while the latter one is always assumed closed.
"""
__author__ = "Konstantin Klementiev"
__date__ = "19 Aug 2024"
import sys
import os, sys; sys.path.append(os.path.join('..', '..'))  # analysis:ignore
import numpy as np

import xrt.backends.raycing as raycing
import xrt.backends.raycing.sources as rs
import xrt.backends.raycing.oes as roe
import xrt.backends.raycing.run as rr
import xrt.plotter as xrtp
import xrt.runner as xrtr
import xrt.backends.raycing.screens as rsc

showIn3D = False

E0, dE = 9000., 5.,
p = 20000.
q = p/2
tubeLengtgh = 10000.
tubeRadius = 50.  # at the center of the capillary

Mirror = roe.HyperbolicMirrorParam
# Mirror = roe.HyperboloidCapillaryMirror


def build_beamline(nrays=1e5):
    beamLine = raycing.BeamLine(height=0)

    sourceCenter = [0., 0., 0.]
    thetaMin = tubeRadius / (p + tubeLengtgh*0.5)
    thetaMax = tubeRadius / (p - tubeLengtgh*0.5)
    rs.GeometricSource(
        beamLine, 'Geometric Source', sourceCenter, nrays=nrays,
        distE='flat', energies=(E0-dE, E0+dE), polarization='horizontal',
        dx=0, dz=0, dy=0, distxprime='annulus', dxprime=(thetaMin, thetaMax))

    focalPoint = [0, p-q, 0]
    if Mirror is roe.HyperbolicMirrorParam:
        mirrorCenter = [0, p, tubeRadius]
        theta1 = np.arctan2(tubeRadius, p)
        theta2 = np.arctan2(tubeRadius, q)
        theta = (theta2+theta1) / 2
        beamLine.hypMirror = Mirror(
            beamLine, 'Hyperboloid Tube Mirror', mirrorCenter, isClosed=True,
            f1=sourceCenter, f2=focalPoint, pitch=theta, isCylindrical=False,
            limPhysY=[-tubeLengtgh/2, tubeLengtgh/2])
    elif Mirror is roe.HyperboloidCapillaryMirror:
        mirrorCenter = [0, p, 0]
        a = ((p**2 + tubeRadius**2)**0.5 - (q**2 + tubeRadius**2)**0.5) / 2
        c = (p-q) / 2
        b = (c**2 - a**2)**0.5
        beamLine.hypMirror = Mirror(
            beamLine, 'Hyperboloid Capillary Mirror', mirrorCenter,
            hyperbolaA=a, hyperbolaB=b, workingDistance=q-tubeLengtgh/2,
            limPhysY=[-tubeLengtgh/2, tubeLengtgh/2])
    else:
        raise ValueError('Unknown mirror class')

    s0, _, _ = beamLine.hypMirror.xyz_to_param(0, 0, 0)
    r0 = beamLine.hypMirror.local_r(s0, 0)
    print('local_r =', r0)
    n0 = beamLine.hypMirror.local_n(s0, 0)
    print('local_n =', n0)
    print('hyperbola a', beamLine.hypMirror.hyperbolaA)
    print('hyperbola b', beamLine.hypMirror.hyperbolaB)
    # hyperbola a 4999.968750341793
    # hyperbola b 17.67754523490408

    beamLine.screen = rsc.Screen(beamLine, 'Movable Screen', focalPoint)
    return beamLine


def run_process(beamLine, shineOnly1stSource=False):
    if showIn3D:
        beamSource = beamLine.sources[0].shine()
        beamMirrorGlobal, beamMirrorlocal = beamLine.hypMirror.reflect(
            beamSource)
        beamScreenAfterReflection = beamLine.screen.expose(beamMirrorGlobal)
        beamScreenAtFocus = beamLine.screen.expose(beamMirrorGlobal)
        outDict = {
            'beamSource': beamSource,
            'beamMirrorlocal': beamMirrorlocal,
            'beamScreenAfterReflection': beamScreenAfterReflection,
            'beamScreenAtFocus': beamScreenAtFocus,
            }
        beamLine.prepare_flow()
    else:
        beamSource = beamLine.sources[0].shine()

        beamLine.screen.center = [0, p, 0]
        beamScreenBeforeReflection = beamLine.screen.expose(beamSource)

        beamMirrorGlobal, beamMirrorlocal = beamLine.hypMirror.reflect(
            beamSource)
        beamScreenAfterReflection = beamLine.screen.expose(beamMirrorGlobal)

        beamLine.screen.center = [0, p-q-10, 0]
        beamScreenBeforeFocus = beamLine.screen.expose(beamMirrorGlobal)

        beamLine.screen.center = [0, p-q, 0]
        beamScreenAtFocus = beamLine.screen.expose(beamMirrorGlobal)

        outDict = {
            'beamSource': beamSource,
            'beamScreenBeforeReflection': beamScreenBeforeReflection,
            'beamMirrorlocal': beamMirrorlocal,
            'beamScreenAfterReflection': beamScreenAfterReflection,
            'beamScreenBeforeFocus': beamScreenBeforeFocus,
            'beamScreenAtFocus': beamScreenAtFocus,
            }
    return outDict
rr.run_process = run_process


def main():
    beamLine = build_beamline()
    if showIn3D:
        beamLine.glow()
        return

    plots = []

    plot = xrtp.XYCPlot('beamScreenBeforeReflection')
    plots.append(plot)

    plot = xrtp.XYCPlot('beamScreenAfterReflection')
    plots.append(plot)

    xaxis = xrtp.XYCAxis(r'$s$', 'mm')
    yaxis = xrtp.XYCAxis(r'$\phi$', 'rad')
    plot = xrtp.XYCPlot('beamMirrorlocal', aspect='auto',
                        xaxis=xaxis, yaxis=yaxis)
    plots.append(plot)

    plot = xrtp.XYCPlot('beamScreenBeforeFocus')
    plots.append(plot)

    xaxis = xrtp.XYCAxis(r'$x$', 'fm')
    yaxis = xrtp.XYCAxis(r'$z$', 'fm')
    plot = xrtp.XYCPlot('beamScreenAtFocus', xaxis=xaxis, yaxis=yaxis)
    plots.append(plot)

    xrtr.run_ray_tracing(plots, repeats=1, beamLine=beamLine)


if __name__ == '__main__':
    main()
