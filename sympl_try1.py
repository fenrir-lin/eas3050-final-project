#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 22:20:11 2017

@author: zifan
"""

# Here, the names model_package, get_initial_state, Radiation, BoundaryLayer,
# DeepConvection, and ImplicitDynamics are placeholders, and do not refer to
# an actual existing package.
from model_package import (
    get_initial_state, Radiation, BoundaryLayer, DeepConvection,
    ImplicitDynamics)
from sympl import (
    AdamsBashforth, PlotFunctionMonitor, UpdateFrequencyWrapper)
from datetime import datetime, timedelta

def my_plot_function(fig, state):
    ax = fig.add_subplot(1, 1, 1)
    ax.set_xlabel('longitude')
    ax.set_ylabel('latitude')
    ax.set_title('Lowest model level air temperature (K)')
    im = ax.pcolormesh(
        state['air_temperature'].to_units('degK').values[0, :, :],
        vmin=260.,
        vmax=310.)
    cbar = fig.colorbar(im)

plot_monitor = PlotFunctionMonitor(my_plot_function)

state = get_initial_state(nx=256, ny=128, nz=64)
state['time'] = datetime(2000, 1, 1)

physics_stepper = AdamsBashforth(
    UpdateFrequencyWrapper(Radiation(), timedelta(hours=2)),
    BoundaryLayer(),
    DeepConvection(),
)
implicit_dynamics = ImplicitDynamics()

timestep = timedelta(minutes=30)
while state['time'] < datetime(2010, 1, 1):
    physics_diagnostics, state_after_physics = physics_stepper(state)
    dynamics_diagnostics, next_state = implicit_dynamics(state_after_physics)
    state_after_physics.update(physics_diagnostics)
    state_after_physics.update(dynamics_diagnostics)
    plot_monitor.store(state_after_physics)
    next_state['time'] = state['time'] + timestep
    state = next_state