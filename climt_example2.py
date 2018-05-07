#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 00:02:07 2017

@author: zifan
"""

import climt
from sympl import PlotFunctionMonitor
import numpy as np
# import time


def plot_function(fig, state):

    fig.set_size_inches(10, 10)

    ax = fig.add_subplot(2, 2, 1)
    state['surface_temperature'].transpose().plot.contourf(ax=ax, levels=16)

    ax = fig.add_subplot(2, 2, 2)
    state['convective_heating_rate'].mean(dim='longitude').transpose().plot.contourf(
        ax=ax, levels=16)

    ax = fig.add_subplot(2, 2, 3)
    state['eastward_wind'].mean(dim='longitude').transpose().plot.contourf(
        ax=ax, levels=16)

    ax = fig.add_subplot(2, 2, 4)
    state['air_temperature'].mean(dim='longitude').transpose().plot.contourf(
        ax=ax, levels=16)

    fig.tight_layout()


# Create plotting object
monitor = PlotFunctionMonitor(plot_function)

# Create components
dycore = climt.GfsDynamicalCore(number_of_longitudes=128,
                                number_of_latitudes=64,
                                number_of_damped_levels=5)

model_time_step = dycore._time_step

convection = climt.EmanuelConvection(convective_momentum_transfer_coefficient=1)
simple_physics = climt.SimplePhysics()

simple_physics = simple_physics.get_prognostic_version(model_time_step)
convection.current_time_step = model_time_step

radiation = climt.GrayLongwaveRadiation()
slab_surface = climt.SlabSurface()

# Create model state
my_state = climt.get_default_state([dycore, radiation, convection, simple_physics, slab_surface],
                                   x=dycore.grid_definition['x'],
                                   y=dycore.grid_definition['y'],
                                   mid_levels=dycore.grid_definition['mid_levels'],
                                   interface_levels=dycore.grid_definition['interface_levels'])

# Set initial/boundary conditions
sw_flux_equator = 300
sw_flux_pole = 0
latitudes = my_state['latitude'].values

sw_flux_profile = sw_flux_equator - (
    (sw_flux_equator - sw_flux_pole)*(np.sin(np.radians(latitudes))**2))

my_state['downwelling_shortwave_flux_in_air'].values[:] = sw_flux_profile[np.newaxis, :, np.newaxis]

my_state['eastward_wind'].values[:] = np.random.randn(*my_state['eastward_wind'].shape)
my_state['air_temperature'].values[:] = 290
my_state['ocean_mixed_layer_thickness'].values[:] = 0.1
my_state['surface_temperature'].values[:] = 290

dycore.prognostics = [simple_physics, slab_surface, radiation, convection]

for i in range(1000):
    output, diag = dycore(my_state)
    my_state.update(output)
    my_state.update(diag)

    if i % 20 == 0:
        monitor.store(my_state)
        print(i, 'max. zonal wind: ', np.amax(my_state['eastward_wind'].values))
        print('max. surf temp: ', my_state['surface_temperature'].max(keep_attrs=True))