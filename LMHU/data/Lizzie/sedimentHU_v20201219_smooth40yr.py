#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Wed Dec 22 16:55:52 EST 2021
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
    print('[da loaded]:', ofile)
    da = xr.open_dataarray(ofile)
else:
    # tc liz
    #ifile = 'normTCcounts_v0719.txt'
    ifile = 'raw/normTCcounts_v1219.txt'
    tc_liz = pd.read_csv(ifile, sep='\s+', index_col=0)
    #ds_liz = xr.Dataset(tc_liz).rename(years='year').pipe(lambda x: x.assign_coords(year=x.year.values.astype('int')))
    da_liz = xr.DataArray(tc_liz, dims=('year', 'member'))
    da_liz = da_liz.assign_coords(year=da_liz.year.astype('int').values)
    # tc jk
    #ifile = 'jknife_v0719.txt'
    ifile = 'raw/jknife_v1219.txt'
    tc_jk = pd.read_csv(ifile, sep='\s+', index_col=0)
    #ds_jk = xr.Dataset(tc_jk).pipe(lambda x: x.assign_coords(year=x.year.values.astype('int')))
    da_jk = xr.DataArray(tc_jk, dims=('year', 'member'))
    da_jk = da_jk.assign_coords(year=da_liz.year.astype('int').values)
    da_jk = da_jk.sortby(da_jk.member)
    
    #concat da_liz and da_jk
    da = xr.concat([da_liz, da_jk], dim='member')
    da.to_dataset(name='sedimentHU').to_netcdf(ofile)
    print('[saved]:', ofile)

 
 
if __name__ == '__main__':
    from wyconfig import * #my plot settings
    plt.close()
    fig, ax = plt.subplots(figsize=(8,4))
    da = da.sel(year=slice(850, None))
    ax.fill_between(da.year, da.isel(member=2), da.isel(member=3), alpha=0.2, color='k', label='lower/upper')
    ax.set_prop_cycle(None)
    for m in da.member.values[4:]:
        da.sel(member=m).plot(label=m, lw=1.5, ax=ax)
    #da.isel(member=slice(4,None)).plot(hue='member', lw=1, ax=ax)
    da.isel(member=0).plot(lw=3, color='k', ls='-', ax=ax, label='all sites')

    ax.legend(ncol=4, loc='upper left')
    ax.set_title('')
    
    #savefig
    if len(sys.argv)>1 and 'savefig' in sys.argv[1:]:
        figname = __file__.replace('.py', f'.png')
        wysavefig(figname)
    tt.check(f'**Done**')
    plt.show()
    
