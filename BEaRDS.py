"""    Broadband Emission and Radio Detection Software
    Copyright (C) 2018  Jarrod Heslop, Cameron Furlong, Matthew Yeatman

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import matplotlib.pyplot as plt
import numpy as np


def separate_freqs(data):
    """
    This function/module will take the Fits file and set up a dictionary of arrays corrolating to the information in the fits 
    file. For our project this will take the first 8 columns which are not measurements and leave them with the Header in the 
    CSV. The rest of the columns > 8 will be converted into Megahertz as a key with relevant data for that key in the value as 
    an array. This makes reading the data easier with numpy. The unit label has been removed from the dictionary keys for use in
    other functions.
    Args:
        data (Pandas CSV): Open your CSV file with the pandas module. Input this file into this function.
    Returns:
        freq_specs (TYPE): The return is a dictionary, first 8 entries are ('Time', 'Time (UTS)', 'Num of Samples', 'Length', 'Had issue',
        'GPS fix', 'GPS LAT', 'GPS LON') then the rest are each of frequencies measured in MHz.
    """
    freq_specs = {}
    start = 0
    for cont in range(0, len(data.columns), 1):
        if data.columns[cont] == '1000000.0':
            start += cont
    # print(start)
    for count in range(0, len(data.columns), 1):
        if count > start-2:
            name = int((float(data.columns[count])/1000000))
            freq_specs[name] = np.asarray(data[data.columns[count]])
        else:
            freq_specs[data.columns[count]] = np.asarray(data[data.columns[count]])
    return freq_specs


def mean_freqs(data):
    """
    Data = CSV
    This takes the data and finds the average of all the values for each frequency.
    Args:
        data (Pandas CSV): Default pandas CSV file
    Returns:
        mean_dic (Dictionary): A dictionary with frequency as a key and the mean of all the data for that frequency as the value.
    """
    mean_dic = {}
    start = 0
    for cont in range(0, len(data.columns), 1):
        if data.columns[cont] == '1000000.0':
            start += cont
    for count in range(0, len(data.columns), 1):
        if count > start-2:
            name = int((float(data.columns[count])/1000000))
            mean_dic['%d MHz' % name] = np.mean(data[data.columns[count]])
    return mean_dic


def mean(data):
    """
    Data = Dictionary
    This takes the data and finds the average for the values of the frequencies.
    Args:
        data (Dictionary): A dictionary of data arrays you want the mean value of.
    Returns:
        mean (Dictionary): Description
    """
    means = {}
    for key, value in data.items():
        if isinstance(key, int):
            means[key] = np.mean(value)
    return means


def pulltargets(targets, data):
    """
    This takes the targets of astronomical research and the redshifting or blueshifting of the data and extracts from 
    the complete data sets taken with the instrumentation.
    Args:
        targets (TYPE): Description
        data (TYPE): Description
    Returns:
        TYPE: Description
    """
    targ_data = {}
    for item in targets:
        for key, value in data.items():
            if key == item:
                targ_data[item] = value
    return targ_data


def KepRot(r_bulge):
    """
    This calculates the velocty of a galaxy based on Keplerian Rotation approximation of a sphere.
    Inputs: r_bulge = float/int.
    Args:
        r_bulge (Float): Radius from center of galaxy to point of interest in Ly
    Returns:
        Velocity (Float): Radial velocity of object at distance in m/s
    """

    G = 6.67e-11
    v = ((4 * np.pi * G * r_bulge * 9.461e15) / 3)**0.5
    return v


def Doppler(f_src, v):
    """
    This calculates the Doppler Shifted frequencies of EM emitted by sources moving away or towards us.
    Input: f_src=1d list, v = velocity = float/int
    Args:
        f_src (Array): An array of frequencies of interest
        v (Float): Radial velocity of object at distance.
    Returns:
        f_final (Array): List of dopplershifted frequencies at the inputted velocity
    """
    c = 299792458
#     f_obs = []
    f_final = []
    for var in f_src:
        f_obs = np.arange(np.floor((c/(c+v))*var*(10**6)), np.ceil((c/(c-v))*var*(10**6)), 1)
        for x in f_obs:
            f_final.append(int(x*(10**-6)))
    f_final = list(set(f_final))
    return f_final


def waterfall_plot(data, dataTitle, ax=None, vmax=0, vmin=-80, nlevels=9):
    """
    The function intakes a HackRF data set and extracts the frequency, intensity, and read count and collates the data into a 
    waterfall plot.
    Input: data=csv file
    Args:
        data (pandas): Pandas RFI data.
        dataTitle (String): Title of plot
        ax (None, optional): used for plotting
        vmax (int, optional): Maximum level for RFI readings
        vmin (TYPE, optional): Minimum level for RFI readings
        nlevels (int, optional): Number of colour levels for colour bar
    Returns:
        TYPE: Description
    """

    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    extracted = separate_freqs(data)
    time = separate_freqs(data)['Time']

    x = []
    y = time
    z = []

    for key, value in extracted.items():
        if isinstance(key, int):
            x.append(key)
            z.append(value)
    z = np.asarray(z)
    x = np.asarray(x)
    y = np.asarray(y)
    p = np.arange(len(y))
    q = np.arange(len(x))
    Y, X = np.meshgrid(p, q)
    print('z', z.shape, 'x', x.shape, 'y', y.shape)

    cf = ax.contourf(X, Y, z, cmap=plt.cm.gnuplot, levels=np.linspace(vmin, vmax, nlevels))
    cf.set_clim(vmin, vmax)
    ax.set_title(dataTitle)
    ax.set_xlabel('Frequency', fontsize=12)
    ax.set_ylabel('Read #', fontsize=12)
    fig.colorbar(cf, boundaries=(vmin, vmax))
    return fig, ax

def waterfall_plot_dict(data, time, dataTitle, ax=None, vmax=0, vmin=-80, nlevels=9):
    """
    The function intakes a HackRF data set and extracts the frequency, intensity, and read count and collates the data into a 
    waterfall plot.
    Input: data=csv file
    Args:
        data (pandas CSV): Pandas RFI data
        dataTitle (String): Title of plot
        time (Array): Array of times of measurement
        ax (None, optional): used for plotting
        vmax (int, optional): Maximum level for RFI readings
        vmin (TYPE, optional): Minimum level for RFI readings
        nlevels (int, optional): Number of colour levels for colour bar
    Returns:
        TYPE: Description
    """

    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

#     time = data['Time']

    x = []
    y = time
    z = []

    for key, value in data.items():
        if isinstance(key, int):
            x.append(key)
            z.append(value)
    z = np.asarray(z)
    x = np.asarray(x)
    y = np.asarray(y)
    p = np.arange(len(y))
    q = np.arange(len(x))
    Y, X = np.meshgrid(p, q)
    print('z', z.shape, 'x', x.shape, 'y', y.shape)

    cf = ax.contourf(X, Y, z, cmap=plt.cm.gnuplot, levels=np.linspace(vmin, vmax, nlevels))
    cf.set_clim(vmin, vmax)
    ax.set_title(dataTitle)
    ax.set_xlabel('Frequency', fontsize=12)
    ax.set_ylabel('Read #', fontsize=12)
    fig.colorbar(cf, boundaries=(vmin, vmax))
    return fig, ax