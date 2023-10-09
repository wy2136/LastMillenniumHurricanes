#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Wed Dec 29 12:57:43 EST 2021
if __name__ == '__main__':
    import sys
    from misc.timer import Timer
    s = ' '
    tt = Timer(f'start {s.join(sys.argv)}')
import sys, os.path, os, glob, datetime
import xarray as xr, numpy as np, pandas as pd, matplotlib.pyplot as plt
#more imports
import xfilter
#
if __name__ == '__main__':
    tt.check('end import')
#
#start from here
n_window = 40 #40-year cutoff period
lowpass = lambda da: da.filter.lowpass(1/n_window, dim='year', padtype='even')
quantiles = [0.025, 0.5, 0.975]
ifile = '/tigress/wenchang/data/vecchi2021data/humh_adjusted.nc'
ofile = __file__.replace('.py', f'{n_window}.nc')
if os.path.exists(ofile):
    ds = xr.open_dataset(ofile)
    print('[loaded]:', ofile)
else:
    ds = xr.open_dataset(ifile)[['HU', 'MH', 'HUlandfall', 'MHlandfall']]
    hu = ds.HU.pipe(lowpass).quantile(quantiles, dim='sample')
    mh = ds.MH.pipe(lowpass).quantile(quantiles, dim='sample')
    hu_landfall = ds.HUlandfall.pipe(lowpass)
    mh_landfall = ds.MHlandfall.pipe(lowpass)
    ds = xr.Dataset(dict(HU=hu, MH=mh, HUlandfall=hu_landfall, MHlandfall=mh_landfall))
    ds.to_netcdf(ofile)
    print('[saved]:', ofile)


 
 
if __name__ == '__main__':
    from wyconfig import * #my plot settings
    fig,ax = plt.subplots()
    daname = 'HU'
    ax.fill_between(ds.year, *ds[daname].sel(quantile=[0.025, 0.975]), alpha=0.2)
    ds[daname].sel(quantile=0.5).plot(label=daname, ax=ax)

    daname = 'MH'
    ax.fill_between(ds.year, *ds[daname].sel(quantile=[0.025, 0.975]), alpha=0.2)
    ds[daname].sel(quantile=0.5).plot(label=daname, ax=ax)
    
    ax_right = ax.twinx()
    daname = 'HUlandfall'
    ds[daname].plot(label=daname, ax=ax_right, ls='--')
    
    daname = 'MHlandfall'
    ds[daname].plot(label=daname, ax=ax_right, ls='--')
    
    ax.legend(loc='upper left')
    ax.set_ylabel('#')
    ax.set_title(f'Adjusted Hurricanes/Major Hurricanes: {n_window}-year lowpass')
    ax_right.legend(loc='upper right')
    ax_right.grid(False)
    ax_right.spines['right'].set_visible(True)
    ax_right.set_ylabel('landfall #')

    #savefig
    if len(sys.argv)>1 and 'savefig' in sys.argv[1:]:
        figname = __file__.replace('.py', f'{n_window}.png')
        if 'overwritefig' in sys.argv[1:]:
            wysavefig(figname, overwritefig=True)
        else:
            wysavefig(figname)
    tt.check(f'**Done**')
    plt.show()
    
