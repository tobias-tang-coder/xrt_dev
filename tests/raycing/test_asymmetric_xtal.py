# -*- coding: utf-8 -*-
r"""
Reflection from asymmetrically cut crystal
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A monochromatic beam of *E* = 2840 eV is diffracted by a Si111 crystal with
θ\ :sub:`B`\ = 44.132 deg and α = -20.054 deg, which results in *b* = -0.453.

The phase space volume in the beam before and after the crystal is indeed
invariant, whereas the linear and angular sizes have scaled with the ratio
equal to *b* or 1/*b*. The product FWHM(z)×FWHM(z') = 135 nmrad in both cases.
Notice also the deviation of the diffracted beam direction from the exact
departure angle 2θ\ :sub:`B` seen on the exit screen which is put normally to
2θ\ :sub:`B` (i.e. z'=0 at the exact departure at 2θ\ :sub:`B`\ ).
The ray-traced deviation -106 µrad is close to the calculated refractive shift
-105 µrad.

.. imagezoom:: _images/0-zzP-source,alpha=-0.350.png
.. imagezoom:: _images/2-zzP-afterXtal,alpha=-0.350.png

"""
__author__ = "Konstantin Klementiev"
__date__ = "2018/02/17"
import sys
import numpy as np

sys.path.append(r"C:\Ray-tracing")
import xrt.backends.raycing.sources as rsources
import xrt.backends.raycing.screens as rscreens
import xrt.backends.raycing.materials as rmats
import xrt.backends.raycing.oes as roes
import xrt.backends.raycing.run as rrun
import xrt.backends.raycing as raycing
import xrt.plotter as xrtplot
import xrt.runner as xrtrun

Ec = 2840
nrays = 1e6

crystalSi = rmats.CrystalSi(geom="Bragg")
#crystalSi = rmats.CrystalSi(geom="Laue", t=0.1)
alpha = -0.35
if crystalSi.geom.startswith("Laue"):
    alpha += np.pi/2


def build_beamline():
    beamLine = raycing.BeamLine()

    beamLine.source = rsources.GeometricSource(
        beamLine, center=[0, 0, 0],
        dx=2, dz=1, dxprime=25e-06, dzprime=25e-06,
        # distE=r"normal", energies=[Ec, 1],
        energies=[Ec],
        nrays=nrays)

    beamLine.screenSource = rscreens.Screen(beamLine, center=[0, 2000, 0])

    bragg = crystalSi.get_Bragg_angle(Ec) - crystalSi.get_dtheta(Ec, alpha)
    b = -np.sin(bragg+alpha) / np.sin(bragg-alpha)
    print('bragg={0:.3f}deg; alpha={1:.3f}deg, b={2:.3f}'.format(
        np.degrees(bragg), np.degrees(alpha), b))
    beamLine.bragg = bragg
    beamLine.xtal = roes.OE(
        bl=beamLine, center=[0, 2000, 0],
        material=crystalSi, pitch=bragg+alpha, alpha=alpha)

    p = 0
    beamLine.screenXtal = rscreens.Screen(
        beamLine, center=[0, 2000+p, p*np.tan(2*bragg)],
        x=[1, 0, 0], z=[0, -np.sin(2*bragg), np.cos(2*bragg)])

    beamLine.dbragg = crystalSi.get_refractive_correction(Ec, alpha=alpha)*1e6
    print(u'refractive shift = {0} µrad'.format(beamLine.dbragg))

    return beamLine


def run_process(beamLine):
    beamSource = beamLine.source.shine()
    beamScreenSource = beamLine.screenSource.expose(beamSource)
    beamXtalGlobal, beamXtalLocal = beamLine.xtal.reflect(beamSource)
    beamScreenXtal = beamLine.screenXtal.expose(beamXtalGlobal)
    outDict = {'beamScreenSource': beamScreenSource,
               'beamXtalLocal': beamXtalLocal,
               'beamScreenXtal': beamScreenXtal}
    return outDict
rrun.run_process = run_process


def define_plots(beamLine):
    plots = []

    plot = xrtplot.XYCPlot(
        beam=r"beamScreenSource",
        xaxis=xrtplot.XYCAxis(r"x", limits=[-5, 5]),
        yaxis=xrtplot.XYCAxis(r"z", limits=[-5, 5]))
    plot.saveName = ["0-xz-source.png".format(alpha)]
    plots.append(plot)

    plot = xrtplot.XYCPlot(
        beam=r"beamScreenSource",
        aspect='auto',
        xaxis=xrtplot.XYCAxis(r"z", "mm", limits=[-5, 5], bins=256, ppb=1),
        yaxis=xrtplot.XYCAxis(r"z'", u"µrad", limits=[-55, 55],
                              bins=256, ppb=1))
    plot.saveName = ["0-zzP-source,alpha={0:.3f}.png".format(alpha)]
    plotPhaseSpaceBefore = plot
    plots.append(plot)

    plot = xrtplot.XYCPlot(
        beam=r"beamXtalLocal",
        xaxis=xrtplot.XYCAxis(r"x", limits=[-5, 5]),
        yaxis=xrtplot.XYCAxis(r"y", limits=[-5, 5]))
    plot.saveName = ["1-xy-XtalLocal,alpha={0:.3f}.png".format(alpha)]
    plots.append(plot)

    plot = xrtplot.XYCPlot(
        beam=r"beamScreenXtal",
        xaxis=xrtplot.XYCAxis(r"x", limits=[-5, 5]),
        yaxis=xrtplot.XYCAxis(r"z", limits=[-5, 5]))
    plot.saveName = ["2-xz-afterXtal,alpha={0:.3f}.png".format(alpha)]
    plots.append(plot)

    ac = beamLine.dbragg
    plot = xrtplot.XYCPlot(
        beam=r"beamScreenXtal",
        aspect='auto',
        xaxis=xrtplot.XYCAxis(r"z", "mm", limits=[-5, 5], bins=256, ppb=1),
        yaxis=xrtplot.XYCAxis(r"z'", u"µrad", limits=[ac-55, ac+55],
                              bins=256, ppb=1))
    plot.saveName = ["2-zzP-afterXtal,alpha={0:.3f}.png".format(alpha)]
    plotPhaseSpaceAfter = plot
    plots.append(plot)

    for plot in plots:
        plot.caxis.offset = Ec
        plot.caxis.limits = [Ec-1, Ec+1]
        plot.xaxis.fwhmFormatStr = '%1.3f'
        plot.yaxis.fwhmFormatStr = '%1.3f'

    return plots, plotPhaseSpaceBefore, plotPhaseSpaceAfter


def afterScript(plotPhaseSpaceBefore, plotPhaseSpaceAfter, beamLine):
    PhaseSpaceVolumeBefore = plotPhaseSpaceBefore.dx * plotPhaseSpaceBefore.dy
    PhaseSpaceVolumeAfter = plotPhaseSpaceAfter.dx * plotPhaseSpaceAfter.dy
    print(u"2θ = {0:.3f} deg".format(np.degrees(2*beamLine.bragg)))
    print("phase space volume before and after = {0:.3f} nm and {1:.3f} nm".
          format(PhaseSpaceVolumeBefore, PhaseSpaceVolumeAfter))


def main():
    beamLine = build_beamline()
    E0 = list(beamLine.source.energies)[0]
    beamLine.alignE = E0
    plots, plotPhaseSpaceBefore, plotPhaseSpaceAfter = define_plots(beamLine)
    xrtrun.run_ray_tracing(
        plots=plots, repeats=1, beamLine=beamLine,
        afterScript=afterScript,
        afterScriptArgs=[plotPhaseSpaceBefore, plotPhaseSpaceAfter, beamLine])


if __name__ == '__main__':
    main()
