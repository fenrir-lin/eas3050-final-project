#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 22:10:14 2017

@author: zifan
"""

import climt
import matplotlib.pyplot as plt
import numpy as np

def try1():
    radiation = climt.GrayLongwaveRadiation()
    surface = climt.SlabSurface()
    state = climt.get_default_state([radiation, surface])
    tendencies, diagnostics = radiation(state)
    
    print tendencies.keys()
    print
    print tendencies['air_temperature']


def try2():
    radiation = climt.GrayLongwaveRadiation()
    condensation = climt.GridScaleCondensation()
    x = dict(label='some_x_coord',
             values=np.linspace(0, 20, 10),
             dims='some_x_coord',
             units='kilometer')
    y = dict(label='some_y_coord',
             values=np.linspace(0, 20, 10),
             dims='some_y_coord',
             units='degrees_north')
    state = climt.get_default_state([radiation], x=x, y=y)
    print state['air_temperature']
    state['air_temperature'].plot()
    plt.show()
    print radiation.tendencies
    print radiation.diagnostics
    print condensation.outputs
    print condensation.diagnostics

def main():
    #try1()
    try2()
    

main()