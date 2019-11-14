import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

plt.ioff()

msfile = sys.argv[-1]
if not os.path.exists(msfile):
    print('No data found')
    data_path = '/home/jmoldon/processing/emerlin/TS8004_C_001_20190801/'
    msname = 'TS8004_C_001_20190801_avg.ms'
    msfile = os.path.join(data_path, msname)

def get_spws(msfile):
    msmd.open(msfile)
    spws = msmd.datadescids()
    freq_spw = {spw:msmd.chanfreqs(spw) for spw in spws}
    freqs = np.concatenate([freq_spw[s] for s in spws])
    msmd.close()
    return spws, freqs

def avg_flags_spw(msfile, spw, scan=None, field=None, bsl=None):
    if scan is not None:
        scan = str(scan)
    bsl = bsl.replace('-', '&')
    ms.open(msfile)
    staql={'spw': str(spw), 'field':field, 'baseline':bsl, 'scan':scan}
    ms.msselect(staql)
    d = ms.getdata(['flag', 'axis_info'])
    ms.close()
    flags = np.average(d['flag'], axis=(0,2))
    freqs = d['axis_info']['freq_axis']['chan_freq'][:,0]
    return flags, freqs


def read_flags(msfile, spws, scan=None, field=None, bsl=None):
    flags = np.array([])
    freqs = np.array([])
    for spw in spws:
        flags_spw, freqs_spw = avg_flags_spw(msfile, spw=spw, bsl=bsl)
        flags = np.concatenate([flags, flags_spw])
        freqs = np.concatenate([freqs, freqs_spw])
    return freqs, flags
    

def get_baselines(msfile):
    msmd.open(msfile)
    antennas0 = msmd.antennanames()
    baselines0 = msmd.baselines()
    baselines = []
    for i, a in enumerate(antennas0):
        for j, b in enumerate(antennas0):
            if j > i:
                baselines.append('{0}-{1}'.format(a, b))
    baselines_id = []
    for bsl in baselines:
        a0_id = np.argwhere(np.array(antennas0) ==bsl.split('-')[0])[0][0]
        a1_id = np.argwhere(np.array(antennas0) ==bsl.split('-')[1])[0][0]
        baselines_id.append('{0}-{1}'.format(a0_id, a1_id))
    return np.array(baselines), np.array(baselines_id)


def plot_flags(freqs, flags_bsl, bsl):
    fig, ax = plt.subplots(1,1, figsize=(14,6))
    ax.fill_between(freqs, flags_bsl, facecolor='0.5')
    ax.set_title(bsl)
    ax.set_xlim(np.min(freqs), np.max(freqs))
    ax.set_ylim(np.min(flags_bsl) ,1)
    maxlocator=MaxNLocator(nbins=9)
    minlocator=MaxNLocator(nbins=9*4)
    ax.xaxis.set_major_locator(maxlocator)
    ax.xaxis.set_minor_locator(minlocator)
    ax.grid(which='both', ls = '-', alpha=0.2, axis='x')
    fig.savefig('flags_{}.png'.format(bsl), bbox_inches='tight')

def plot_all_flags(data, baselines):
    fig, ax = plt.subplots(nrows=len(baselines), 
                           ncols=1,
                           figsize=(14,2*len(baselines)),
                           sharex=True)
    maxlocator=MaxNLocator(nbins=9)
    minlocator=MaxNLocator(nbins=9*4)
    for i, ax in enumerate(ax):
        ax.fill_between(data[:,0], data[:,i+1], facecolor='0.5')
        ax.set_title(baselines[i])
        ax.set_xlim(np.min(data[:,0]), np.max(data[:,0]))
        ax.set_ylim(np.min(data[:,i+1]),1)
        ax.xaxis.set_major_locator(maxlocator)
        ax.xaxis.set_minor_locator(minlocator)
        ax.grid(which='both', ls = '-', alpha=0.2, axis='x')
    fig.savefig('flags_{}.png'.format('all'), bbox_inches='tight')

baselines, baselines_id = get_baselines(msfile)

spws, freqs_ms = get_spws(msfile)
data = np.zeros((len(freqs_ms), len(baselines)+1))
# First column for the frequencies
data[:,0] = freqs_ms/1e9
for i, bsl in enumerate(baselines):
    print(bsl)
    freqs, flags_bsl = read_flags(msfile, spws=spws, bsl=bsl)
    plot_flags(freqs/1e9, flags_bsl, bsl)
    data[:,i+1] = flags_bsl

plot_all_flags(data, baselines)
header =  'freq,' + ','.join([bsl for bsl in baselines])
fileout = 'flags.csv'
np.savetxt(fileout, data, delimiter=',', fmt='%6.4f', header=header)


