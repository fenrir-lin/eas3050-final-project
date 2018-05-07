#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 22:44:38 2017

@author: zifan
"""

import climt
import matplotlib.pyplot as plt
import numpy as np
from sympl import AdamsBashforth
from datetime import timedelta

incoming_radiation = climt.RRTMGShortwave(
        cloud_overlap_method=0,
        solar_constant = 2500)
outgoing_radiation = climt.RRTMGLongwave(
        cloud_overlap_method=0)
convection = climt.EmanuelConvection()
surface = climt.SlabSurface()
state = climt.get_default_state([incoming_radiation,
                                 outgoing_radiation,
                                 convection])
model_time_step = timedelta(hours=24)
model = AdamsBashforth([incoming_radiation,
                        outgoing_radiation,
                        convection])

for step in range(50):
    diagnostics, new_state = model(state, model_time_step)
    state.update(diagnostics)
    state.update(new_state)
    state['time'] += model_time_step
    print state['time'], ':', state['air_temperature'].max().values
    #print state['time'], ':', state['surface_longwave_emissivity'].max().values

#print state.keys()