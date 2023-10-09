#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Sun Jan  9 00:06:25 EST 2022
if __name__ == '__main__':
    import sys
    from misc.timer import Timer
    tt = Timer('start ' + ' '.join(sys.argv))
import sys, os.path, os, glob, datetime
import xarray as xr, numpy as np, pandas as pd, matplotlib.pyplot as plt
#more imports
import xfilter
n_window = 40
lowpass = lambda da: da.filter.lowpass(1/n_window, dim='year', padtype='even')
#
if __name__ == '__main__':
    tt.check('end import')
#
#start from here
#params from sys.argv
ifile = 'LME_sstTC_850forcing.nc' if len(sys.argv)>1 and '850forcing' in sys.argv[1:] else 'LME_sstTC_0850cntl.nc'
#daname = 'MH' if len(sys.argv)>1 and 'MH' in sys.argv[1:] else 'HU'
daname = 'HU'
if len(sys.argv)>1:
    if 'MH' in sys.argv[1:]:
        daname = 'MH'
    elif 'rMDRa' in sys.argv[1:]:
        daname = 'rMDRa'
    elif 'TROPa' in sys.argv[1:]:
        daname = 'TROPa'
print(f'{daname = }')

ofile = ifile.replace('.nc', f'_{daname}_smooth{n_window}yr_spread.nc')
if os.path.exists(ofile):
    print('[exists]:', ofile)
    sys.exit()
else:
    if daname == 'rMDRa':
        ds_ = xr.open_dataset(ifile)
        da = ds_['MDRa'] - ds_['TROPa']
    else:
        da = xr.open_dataset(ifile)[daname]
    if daname in ('HU', 'MH'):
        #MC runs for HU and MH
        rng = np.random.default_rng(20220109)
        zz = rng.poisson(da, size=(10000,)+da.shape)
        da_mc = xr.DataArray(zz, dims=('mcrun',)+da.dims).assign_coords(year=da.year.values).pipe(lowpass)
        da_spread = da_mc.quantile([0.025, 0.5, 0.975], dim=['mcrun', 'year'])
        da_mean = da_mc.mean(['mcrun', 'year'])
        da_mean = da_mean.expand_dims('quantile').assign_coords(quantile=[2,])
    else:
        #for rMDRa, TROPa
        da_lp = da.pipe(lowpass)
        da_spread = da_lp.quantile([0.025, 0.5, 0.975], dim='year')
        da_mean = da_lp.mean('year')
        da_mean = da_mean.expand_dims('quantile').assign_coords(quantile=[2,])
    da = xr.concat([da_spread, da_mean], dim='quantile')
    da.attrs['note'] = 'quantile=2 is mean'
    da.to_dataset(name=daname).to_netcdf(ofile)
    print('[saved]:', ofile)

 
 
if __name__ == '__main__':
    #from wyconfig import * #my plot settings
    
    #savefig
    if len(sys.argv)>1 and 'savefig' in sys.argv[1:]:
        figname = __file__.replace('.py', f'.png')
        if 'overwritefig' in sys.argv[1:]:
            wysavefig(figname, overwritefig=True)
        else:
            wysavefig(figname)
    tt.check(f'**Done**')
    #plt.show()
    
