# -*- coding: utf-8 -*-
"""

__author__ = "Konstantin Klementiev", "Roman Chernikov"
__date__ = "2024-06-28"

Created with xrtQook




"""

import numpy as np
import sys
sys.path.append(r"C:\Users\zengguang\miniconda3\envs\xrt_tang\lib\site-packages")
import xrt.backends.raycing.sources as rsources
import xrt.backends.raycing.screens as rscreens
import xrt.backends.raycing.materials as rmats
import xrt.backends.raycing.oes as roes
import xrt.backends.raycing.apertures as rapts
import xrt.backends.raycing.run as rrun
import xrt.backends.raycing as raycing
import xrt.plotter as xrtplot
import xrt.runner as xrtrun
import matplotlib


mGolden = rmats.Material(
    elements=r"Au",
    kind=r"mirror",
    rho=19.32)

def build_beamline():
    beamLine = raycing.BeamLine()

    beamLine.geometricSource01 = rsources.GeometricSource(
        bl=beamLine,
        center=[0, 0, 0],
        nrays=500000,
        dx=0.028,
        dz=0.008,
        dxprime=0.0001,
        dzprime=0.0001,
        energies=[300.0])

    beamLine.rectangularAperture01 = rapts.RectangularAperture(
        bl=beamLine,
        center=[0, 7000, 0],
        opening=[-1000, 1000, -1.09, 1.09]
        )

    beamLine.woltermonolithicMirrorParam01 = roes.WoltermonolithicMirrorParam(
        bl=beamLine,
        center=[0, 8843.638839451649, 0],
        pitch=0.01756675958686552,
        material=mGolden,
        limPhysX=[-1000.0, 1000.0],
        limPhysY=[-76.5, 133.5],


        isClosed = True,
        workingDistance=25,
        Lsf=9000,
        Lmi=210,
        M=115,
        tNA = np.arctan(6.045408722331921*0.5/25),
        f1=[0, 0, 0])

    beamLine.screen01 = rscreens.Screen(
        bl=beamLine,
        center=[0, 8.999996310235625e+03, 8.149585451703967e+00])

    return beamLine


def run_process(beamLine):
    np.random.seed(0)
    geometricSource01beamGlobal01 = beamLine.geometricSource01.shine()

    rectangularAperture01beamLocal01 = beamLine.rectangularAperture01.propagate(
        beam=geometricSource01beamGlobal01)

    woltermonolithicMirrorParam01beamGlobal01, woltermonolithicMirrorParam01beamLocal01 = beamLine.woltermonolithicMirrorParam01.multiple_reflect(
        beam=geometricSource01beamGlobal01, maxReflections=10)

    screen01beamLocal01 = beamLine.screen01.expose(
        beam=woltermonolithicMirrorParam01beamGlobal01)


    outDict = {
        'geometricSource01beamGlobal01': geometricSource01beamGlobal01,
        'rectangularAperture01beamLocal01': rectangularAperture01beamLocal01,
        'woltermonolithicMirrorParam01beamGlobal01': woltermonolithicMirrorParam01beamGlobal01,
        'woltermonolithicMirrorParam01beamLocal01': woltermonolithicMirrorParam01beamLocal01,
        'screen01beamLocal01': screen01beamLocal01}
    return outDict


rrun.run_process = run_process


def define_plots():
    plots = []

    plot01 = xrtplot.XYCPlot(
        beam=r"rectangularAperture01beamLocal01",
        xaxis=xrtplot.XYCAxis(
            label=r"x",
            unit=r"mm"),
        yaxis=xrtplot.XYCAxis(
            label=r"z",
            unit=r"mm"),
        caxis=xrtplot.XYCAxis(
            label=r"energy",
            unit=r"eV"),
        aspect=r"auto",
        title=r"aperture plot")
    plots.append(plot01)

    plot02 = xrtplot.XYCPlot(
        beam=r"screen01beamLocal01",
        xaxis=xrtplot.XYCAxis(
            label=r"x",
            unit=r"nm"),
        yaxis=xrtplot.XYCAxis(
            label=r"z",
            unit=r"nm"),
        caxis=xrtplot.XYCAxis(
            label=r"energy",
            unit=r"eV"),
        aspect=r"auto",
        title=r"sample plot")
    plots.append(plot02)

    plot03 = xrtplot.XYCPlotWithNumerOfReflections(
    'screen01beamLocal01', (1, 2),
    xaxis=xrtplot.XYCAxis(r'x', 'nm', limits=[-1000, 1000]), aspect='auto',
    yaxis=xrtplot.XYCAxis(r'z', 'nm', limits=[-1000, 1000]),
    caxis=xrtplot.XYCAxis('number of reflections', '',  bins=32, ppb=8,
                        data=raycing.get_reflection_number),
    title='reflect with number of reflections')
    plot03.caxis.fwhmFormatStr = None
    plots.append(plot03)

    plot04 = xrtplot.XYCPlotWithNumerOfReflections(
    'woltermonolithicMirrorParam01beamLocal01', (1,),
    xaxis=xrtplot.XYCAxis(r'x', 'mm', limits=[-5,5]), aspect='auto',
    yaxis=xrtplot.XYCAxis(r'y', 'mm', limits=[-90,140]),
    caxis=xrtplot.XYCAxis('number of reflections', '',  bins=32, ppb=8,
                        data=raycing.get_reflection_number),
    title='wolter local beam')
    plot04.caxis.fwhmFormatStr = None
    plots.append(plot04)   
    
    return plots


def main():
    beamLine = build_beamline()
    E0 = list(beamLine.geometricSource01.energies)[0]
    beamLine.alignE=E0
    plots = define_plots()
    xrtrun.run_ray_tracing(
        plots=plots,
        backend=r"raycing",
        beamLine=beamLine)

if __name__ == '__main__':
    main()
