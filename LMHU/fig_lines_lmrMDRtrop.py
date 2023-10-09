#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Fri Dec 31 10:58:52 EST 2021
if __name__ == '__main__':
    import sys
    from misc.timer import Timer
    s = ' '
    tt = Timer(f'start {s.join(sys.argv)}')
import sys, os.path, os, glob, datetime
import xarray as xr, numpy as np, pandas as pd, matplotlib.pyplot as plt
#more imports
import xfilter
n_window = 40 #lowpass cutoff years
lowpass = lambda da: da.filter.lowpass(1/n_window, dim='year', padtype='even')
from misc.shell import run_shell
#
if __name__ == '__main__':
    tt.check('end import')
#
#start from here
#ds_lmr2018 = xr.open_dataset('data/LMR/LMR2018_sstmdrtrop_rMDRtransformed18702000.nc')
#ds_lmr2019 = xr.open_dataset('data/LMR/LMR2019_sstmdrtrop_rMDRtransformed18702000.nc')
#LMR2018
ifile = 'data/LMR/LMR2018_sstmdrtrop_rMDRtransformed18702000.nc'
ifile_cached = __file__.replace('.py', '__LMR2018.nc')
if not os.path.exists(ifile_cached): run_shell(f'cp {ifile} {ifile_cached}')
ds_lmr2018 = xr.open_dataset(ifile_cached)
print('[loaded]:', ifile_cached)
#LMR2019
ifile = 'data/LMR/LMR2019_sstmdrtrop_rMDRtransformed18702000.nc'
ifile_cached = __file__.replace('.py', '__LMR2019.nc')
if not os.path.exists(ifile_cached): run_shell(f'cp {ifile} {ifile_cached}')
ds_lmr2019 = xr.open_dataset(ifile_cached)
print('[loaded]:', ifile_cached)

def wyplot(ax=None):
    if ax is None: fig, ax = plt.subplots(figsize=(8,3))
    alpha = 0.1
    years = slice(850, 2000)
    #LMR2018: LMR2.0
    MDR = ds_lmr2018['MDR'].sel(year=years)
    TROP = ds_lmr2018['TROP'].sel(year=years)
    rMDR = (MDR - TROP).pipe(lowpass)
    MDR = MDR.pipe(lowpass)
    TROP = TROP.pipe(lowpass)
    #rMDR
    mean = rMDR.mean('MCrun')
    std = rMDR.std('MCrun')
    ax.fill_between(mean.year, mean-std, mean+std, color='C0', alpha=alpha)
    line_rMDR_2018 = mean.plot(color='C0', ls='-', label='LMR2.0 MDR-TROP')
    #MDR
    mean = MDR.mean('MCrun')
    std = MDR.std('MCrun')
    ax.fill_between(mean.year, mean-std, mean+std, color='C0', alpha=alpha)
    line_MDR_2018 = mean.plot(color='C0', ls='--', label='LMR2.0 MDR')
    #TROP
    mean = TROP.mean('MCrun')
    std = TROP.std('MCrun')
    ax.fill_between(mean.year, mean-std, mean+std, color='C0', alpha=alpha)
    line_TROP_2018 = mean.plot(color='C0', ls=':', label='LMR2.0 TROP')
   
    #LMR2019: LMR2.1
    MDR = ds_lmr2019['MDR'].sel(year=years)
    TROP = ds_lmr2019['TROP'].sel(year=years)
    rMDR = (MDR - TROP).pipe(lowpass)
    MDR = MDR.pipe(lowpass)
    TROP = TROP.pipe(lowpass)
    #rMDR
    mean = rMDR.mean('MCrun')
    std = rMDR.std('MCrun')
    ax.fill_between(mean.year, mean-std, mean+std, color='C1', alpha=alpha)
    line_rMDR_2019 = mean.plot(color='C1', ls='-', label='LMR2.1 MDR-TROP')
    #MDR
    mean = MDR.mean('MCrun')
    std = MDR.std('MCrun')
    ax.fill_between(mean.year, mean-std, mean+std, color='C1', alpha=alpha)
    line_MDR_2019 = mean.plot(color='C1', ls='--', label='LMR2.1 MDR')
    #TROP
    mean = TROP.mean('MCrun')
    std = TROP.std('MCrun')
    ax.fill_between(mean.year, mean-std, mean+std, color='C1', alpha=alpha)
    line_TROP_2019 = mean.plot(color='C1', ls=':', label='LMR2.1 TROP')

    ax.legend(handles=line_rMDR_2018 + line_rMDR_2019 + line_MDR_2018 + line_MDR_2019 + line_TROP_2018 + line_TROP_2019,
        ncol=3, loc='upper right') 
    ax.set_xlim(years.start, years.stop)
    ax.set_xticks(range(2000,850,-100))
    ax.set_ylim(-0.6, 0.6)
    ax.set_ylabel('K')
    ax.axhline(0, color='gray', ls='--')
    ax.set_title('MDR and tropical mean SST anomalies from LMR', loc='left')
 
if __name__ == '__main__':
    from wyconfig import * #my plot settings
    plt.close()
    wyplot()
    
    #savefig
    if len(sys.argv)>1 and 'savefig' in sys.argv[1:]:
        figname = __file__.replace('.py', f'.png')
        wysavefig(figname)
    tt.check(f'**Done**')
    plt.show()
    
