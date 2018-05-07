#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 12:13:44 2017

@author: zifan
"""

#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 00:17:36 2017

@author: zifan
"""

import math
from sympl import (
    AdamsBashforth, PlotFunctionMonitor)
from climt import RRTMGShortwave, RRTMGLongwave, get_default_state
import numpy as np
from datetime import timedelta
#import matplotlib


def plot_function(fig, state):
    #print "fig: ", type(fig)
    ax = fig.add_subplot(1, 2, 1)
    #print "ax: ", type(ax)
    ax.plot(
        state['shortwave_heating_rate'].values.flatten(),
        state['air_pressure'].values.flatten(), 'r-o')
    ax.axes.invert_yaxis()
    ax.plot(
        state['longwave_heating_rate'].values.flatten(),
        state['air_pressure'].values.flatten(), '-o')
    ax.axes.invert_yaxis()
    ax.set_title('Heating Rates')
    ax.grid()
    ax.set_xlabel('K/day')
    ax.set_ylabel('millibar')

    ax.set_yscale('log')
    ax.set_ylim(1e5, 1.)
    ax = fig.add_subplot(1, 2, 2)
    ax.plot(
        state['air_temperature'].values.flatten(),
        state['air_pressure'].values.flatten(), '-o')
    ax.axes.invert_yaxis()

    ax.set_yscale('log')
    ax.set_ylim(1e5, 1.)
    ax.set_title('Temperature')
    ax.grid()
    ax.set_xlabel('K')
    ax.set_yticklabels([])
    
    
def solarConstant(distance):
    Lsun = 3.828e26
    AU = 149597870700.0
    distance = distance*AU
    return Lsun / (4*math.pi*distance**2.0)


def getAU(lum):
    Lsun = 3.828e26
    AU = 149597870700.0
    return math.sqrt(Lsun / (4*math.pi*lum)) / AU


monitor = PlotFunctionMonitor(plot_function)
rad_sw = RRTMGShortwave(cloud_overlap_method=0, solar_constant=solarConstant(0.65))
rad_lw = RRTMGLongwave(cloud_overlap_method=0)
time_stepper = AdamsBashforth([rad_sw, rad_lw])
timestep = timedelta(hours=1)

mid_levels = {'label': 'mid_level',
              'values': np.arange(60),
              'units': ''}

int_levels = {'label': 'interface_level',
              'values': np.arange(61),
              'units': ''}
state = get_default_state([rad_sw, rad_lw], mid_levels=mid_levels, interface_levels=int_levels)

tp_profiles = np.load('thermodynamic_profiles.npz')
mol_profiles = np.load('molecule_profiles.npz')
co2_input_array = mol_profiles["carbon_dioxide"]

state["g"] = 25.0

#pressure_profile = tp_profiles['air_pressure']
pressure_profile = np.array([  1.00110000e+06,   9.77330000e+04,   9.53550000e+04,
         9.29780000e+04,   9.06060000e+04,   8.82230000e+04,
         8.58450000e+04,   8.34680000e+04,   8.10950000e+04,
         7.87130000e+04,   7.63360000e+04,   7.39580000e+04,
         7.15880000e+04,   6.92020000e+04,   6.68250000e+04,
         6.44480000e+04,   6.20700000e+04,   5.96920000e+04,
         5.73150000e+04,   5.49400000e+04,   5.25590000e+04,
         5.01840000e+04,   4.78040000e+04,   4.54270000e+04,
         4.30570000e+04,   4.06710000e+04,   3.83030000e+04,
         3.59160000e+04,   3.35400000e+04,   3.11610000e+04,
         2.87960000e+04,   2.64050000e+04,   2.40300000e+04,
         2.16360000e+04,   1.90790000e+04,   1.67340000e+04,
         1.44010000e+04,   1.21360000e+04,   9.76940000e+03,
         7.38710000e+03,   5.31150000e+03,   3.78360000e+03,
         2.69790000e+03,   1.92370000e+03,   1.37160000e+03,
         9.78000000e+02,   6.97290000e+02,   4.97120000e+02,
         3.54400000e+02,   2.52700000e+02,   1.80050000e+02,
         1.28320000e+02,   9.15860000e+01,   6.52150000e+01,
         4.65440000e+01,   3.31380000e+01,   2.36710000e+01,
         1.68350000e+01,   1.20410000e+01,   5.00640010e+00])
state['air_pressure'].values[0, 0, :] = pressure_profile
state['air_pressure_on_interface_levels'].values[0, 0, :] = tp_profiles['interface_pressures']

co2_array = np.ones(60)*1e-1  #The mixing ratio of CO2 is varied between 10−5 and 10−1
#specific humidity can range from 0.001g/kg (1e-6) to 12g/kg (1.2e-2)
state['specific_humidity'].values[0, 0, :] = mol_profiles['specific_humidity']*1.2e-2
state['mole_fraction_of_carbon_dioxide_in_air'].values[0, 0, :] = co2_array
#state['specific_humidity'].values[0, 0, :] = mol_profiles['specific_humidity']*1e-3
#state['mole_fraction_of_carbon_dioxide_in_air'].values[0, 0, :] = mol_profiles['carbon_dioxide']
state['Hslab'] = 0.5  # usually set to 0.5
#state["surface_albedo_for_direct_shortwave"] = 0.2  # can range from 0.2 to 0.8, which is not realistic
#state['surface_temperature'].values[:] = 300.0
#state['scon'] = solarConstant(100)

#print "specific humidity", 1e-5, "carbon dioxide is ones"
for i in range(12000):

    #fig = matplotlib.figure.Figure()
    diagnostics, new_state = time_stepper(state, timestep)
    state.update(diagnostics)
    if i % 10 == 0:
        #plot_function(fig,state)
        monitor.store(state)
        folder = "0.65AU_co2Highest_humidityHighest"
        monitor._fig.savefig("plots/"+folder+"/model_try1_"+str(i/10)+".jpg")
    state = new_state
#    if i%20 == 0:
#        print i, "/ 100"


