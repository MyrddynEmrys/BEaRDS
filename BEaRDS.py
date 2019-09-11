"""Summary
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
        data (TYPE): Description

    Returns:
        TYPE: Description
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
        data (TYPE): Description

    Returns:
        TYPE: Description
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
        data (TYPE): Description

    Returns:
        TYPE: Description
    """
    means = {}
    for key, value in data.items():
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
        r_bulge (TYPE): Description

    Returns:
        TYPE: Description
    """

    G = 6.67e-11
    v = ((4 * np.pi * G * r_bulge * 9.461e15) / 3)**0.5
    return v


def Doppler(f_src, v):
    """
    This calculates the Doppler Shifted frequencies of EM emitted by sources moving away or towards us.
    Input: f_src=1d list, v = velocity = float/int

    Args:
        f_src (TYPE): Description
        v (TYPE): Description

    Returns:
        TYPE: Description
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
        dataTitle (TYPE): Description
        ax (None, optional): Description
        vmax (int, optional): Description
        vmin (TYPE, optional): Description
        nlevels (int, optional): Description

    Returns:
        TYPE: Description
    """

    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    extracted = separate_freqs(data)
    time = beards.separate_freqs(data)['Time']

    x = []
    y = time
    z = []

    for key, value in extracted.items():
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
    ax.set_xlabel('Frequency', fontsize=12, color='red')
    ax.set_ylabel('Read #', fontsize=12, color='red')
    fig.colorbar(cf, boundaries=(vmin, vmax))
    return fig, ax
