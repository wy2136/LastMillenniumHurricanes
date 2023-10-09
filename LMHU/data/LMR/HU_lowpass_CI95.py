#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Thu Dec 30 12:45:38 EST 2021
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
ifile = sys.argv[1] if len(sys.argv)>1 else 'LMR2018_ssttc_rMDRtransformed18702000.nc'
daname = 'HU'
n_window = 40 #lowpass cutoff window
lowpass = lambda da: da.filter.lowpass(1/n_window, dim='year', padtype='even')
ofile = ifile.replace('.nc', f'_{daname}_lp{n_window}_CI95.nc')
if os.path.exists(ofile):
    ds = xr.open_dataset(ofile)
    print('[loaded]:', ofile)
else:
    rng = np.random.default_rng(0)
    qq = [0.025, 0.5, 0.975]
    da = xr.open_dataset(ifile)[daname]
    attrs = da.attrs
    zz = rng.poisson(da, size=(10000,)+da.shape)
    da = xr.DataArray(zz, dims=('sample',)+da.dims).assign_coords(year=da.year.values, MCrun=da.MCrun.values).stack(s=('sample', 'MCrun'))
    da = da.pipe(lowpass).quantile(qq, dim='s') 
    da.attrs = attrs
    da.attrs['note'] = f'{daname} from {ifile}, lowpass{n_window}'
    ds = da.to_dataset(name=daname)
    ds.to_netcdf(ofile)
    print('[saved]:', ofile)

 
 
if __name__ == '__main__':
    from wyconfig import * #my plot settings
    fig, ax = plt.subplots()
    da = ds[daname]
    ax.fill_between(da.year, *da.sel(quantile=[0.025,0.975]), alpha=0.2)
    da.sel(quantile=0.5).plot()

    ax.set_title(f'{ifile[:7]} {daname} lowpass{n_window}')
    
    #savefig
    if len(sys.argv)>1 and 'savefig' in sys.argv[1:]:
        #figname = __file__.replace('.py', f'.png')
        figname = ofile.replace('.nc', f'.png')
        wysavefig(figname)
    tt.check(f'**Done**')
    plt.show()
    
