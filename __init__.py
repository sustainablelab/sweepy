'''Control the monochromator to do a wavelength sweep.

Usage
-----
>>> from sweepy.monosweep import MonoSweep
>>> import monochromator as mon # to get usb_handle
>>> with mon.usb.open_monochromator() as mono:
>>>     sweep = MonoSweep(
>>>         usb_handle=mono,
>>>         start_nm=300,
>>>         stop_nm=550,
>>>         step_nm=50
>>>         )

Dependencies
------------
sweepy depends on package `monochromator`

Contents
--------
sweepy contains two modules:

    sweep.py
    --------
    Define base class `Sweep`.
    For setting up sweep parameters.
    Not very useful on its own.

    monosweep.py
    ------------
    Define multiple inheritance class `MonoSweep`
    `MonoSweep` is derived from:
    `monochromator.Monochromator`
    `sweep.Sweep`
    
    Instantiate `MonoSweep` to control the monochromator for a wavelength sweep.

'''
from . import sweep
from . import monosweep
