#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Wed Dec 29 16:49:37 EST 2021
if __name__ == '__main__':
    import sys
    from misc.timer import Timer
    s = ' '
    tt = Timer(f'start {s.join(sys.argv)}')
import sys, os.path, os, glob, datetime
import xarray as xr, numpy as np, pandas as pd, matplotlib.pyplot as plt
#more imports
#
if __name__ == '__main__':
    tt.check('end import')
#
#start from here
ofile = __file__.replace('.py', '.nc')
if os.path.exists(ofile):
    ds = xr.open_dataset(ds)
    print('[loaded]:', ofile)
else:
    #sedient HU
    ifile = 'sedimentHU_smooth40yr_v20211203.nc'
    da = xr.open_dataarray(ifile)
    #adjusted HU records
    ifile_gv = '../Vecchi2021/humh_adjusted_lowpass40.nc'
    da_gv = xr.open_dataset(ifile_gv)['HU']
    yearspan = slice(1870,2000)
    #shift and scale sediment HU to HU count
    selfMean = da.sel(year=yearspan, member='sediment_estimate').mean('year')
    selfSTD = da.sel(year=yearspan, member='sediment_estimate').std('year')
    targetMean = da_gv.sel(year=yearspan, quantile=0.5).mean('year')
    targetSTD = da_gv.sel(year=yearspan, quantile=0.5).std('year')
    da = (da - selfMean)/selfSTD * targetSTD + targetMean
    #save results 
    ds = xr.Dataset(dict(sedimentHUcount=da, HUrecord=da_gv))
    ds.attrs['note'] = f'sedimentHUcount is sedimentHU shifted and scaled so that it shares the same mean/std as HUrecord over the period of {yearspan.start}-{yearspan.stop}.'
    ds.to_netcdf(ofile)
    print('[saved]:', ofile)
 
 
if __name__ == '__main__':
    from wyconfig import * #my plot settings
    plt.close()
    fig, ax = plt.subplots(figsize=(8,4))
    da = ds.sedimentHUcount.sel(year=slice(850, 2000))
    ax.fill_between(da.year, da.isel(member=1), da.isel(member=2), alpha=0.2, color='gray')#, label='lower/upper')
    ax.set_prop_cycle(None)
    for m in da.member.values[3:]:
        da.sel(member=m).plot(label=m, lw=1.5, ax=ax)
    #da.isel(member=slice(4,None)).plot(hue='member', lw=1, ax=ax)
    da.isel(member=0).plot(lw=3, color='gray', ls='-', ax=ax, label='all sites')
    
    da_gv = ds.HUrecord.sel(year=slice(1870,2000))
    ax.fill_between(da_gv.year, *da_gv.sel(quantile=[0.025, 0.975]), alpha=0.2, color='k')
    da_gv.sel(quantile=0.5).plot(lw=3, color='k', ls='-', ax=ax, label='HU records')

    ax.legend(ncol=4, loc='upper left')
    ax.set_ylabel('HU count')
    ax.set_title('')
    
    #savefig
    if len(sys.argv)>1 and 'savefig' in sys.argv[1:]:
        figname = __file__.replace('.py', f'.png')
        wysavefig(figname)
    tt.check(f'**Done**')
    plt.show()
    
