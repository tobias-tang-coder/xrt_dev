This repository is forked from xrt (https://badge.fury.io/gh/kklmn%2Fxrt)
, and expanded some functions. For example, Wolter mirror optical element.

Package xrt (XRayTracer) is a python software library for ray tracing and wave
propagation in x-ray regime. It is primarily meant for modeling synchrotron
sources, beamlines and beamline elements. Includes a GUI for creating a
beamline and interactively viewing it in 3D.

## Install xrt_dev package
Download code and unzip the .zip file into a suitable directory.
In a conda environment or create a new environment running(type) "python setup.py install" from the directory where you have unzipped the archive.

```shell
cd xrt_dev-xrt_modify
python setup.py install
```
note: you may need to install other dependencies, such as numpy, matplotlib, scipy. They are pip installable.

## Usage
### Use written python scripts
example 1:
```shell
python example_wolter_mirror.py
```
example 2: 
```shell
python ./examples/withRaycing/10_MultipleReflect/Cylinder.py
```
### Use xrtQook--the main GUI to xrt
See the documentation on http://xrt.readthedocs.io 
[![Documentation Status](https://readthedocs.org/projects/xrt/badge/?version=latest)](http://xrt.readthedocs.io/?badge=latest) 

### Running xrt without installation
Because xrt does not build anything at the installation time, it can be used without installation, only its source code is required. For running xrt without installation, all required dependencies must be installed beforehand. Look into xrt’s setup.py and find those dependencies in the lists install_requires and extras_require. They are pip installable.

Unzip the .zip file into a suitable directory and use sys.path.append(path-to-xrt) in your script. 
