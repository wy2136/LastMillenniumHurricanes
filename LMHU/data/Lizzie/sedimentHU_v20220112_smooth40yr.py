#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Tue Dec 21 17:08:00 EST 2021
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
ifile = 'raw/2022-01-12/sedimentHU_v20220112_noCaySal_smooth40yr.csv'
if len(sys.argv)>1:
    if 'wCaySal' in sys.argv[1:]: 
        ifile = ifile.replace('noCaySal', 'wCaySal')
    elif 'noCaySal_noCaicos' in sys.argv[1:]: 
        ifile = ifile.replace('noCaySal', 'noCaySal_noCaicos')
    #version 2022-01-12 does not have MH yet
    #if 'MH' in sys.argv[1:]: 
    #    ifile = ifile.replace('HU', 'MH').replace('_noCaySal_', '_')
ofile = os.path.basename(ifile).replace('.csv', '.nc')
if os.path.exists(ofile):
    da = xr.open_dataarray(ofile)
    print('[da loaded]:', ofile)
else: #convert csv file to nc file
    df = pd.read_csv(ifile, index_col=0)
    #rename index
    df.index.name = 'year'
    #rename columns
    columns = df.columns.values
    columns = ['_'.join(s.lower().split()) if s.endswith('estimate') else s for s in columns ] # 'sediment estimate'-> 'sediment_estimate'; 'Upper estiamte'>'upper_estiamte'
    columns = ['no' + ''.join(s[0:-1].split()[1:]) if s.startswith("'No") else s for s in columns ] #e.g. "'No Gulf App Bay'" -> "noGulfAppBay"
    df.columns = columns
    #convert to dataarray
    da = xr.DataArray(df, dims=('year', 'member'))
    da_jk = da.isel(member=slice(3,None)) #jack-knife members
    da_jk = da_jk.sortby(da_jk.member) #sort jk members alphabetically
    da = xr.concat([da.isel(member=slice(0,1)), da.isel(member=slice(2,3)), da.isel(member=slice(1,2)), da_jk], dim='member')
    da.to_dataset(name='sedimentHU').to_netcdf(ofile)
    print('[saved]:', ofile)

if __name__ == '__main__':
    from wyconfig import * #my plot settings
    plt.close()
    fig, ax = plt.subplots(figsize=(8,4))
    da = da.sel(year=slice(850, None))
    ax.fill_between(da.year, da.isel(member=1), da.isel(member=2), alpha=0.1, color='k', label='lower/upper')
    ax.set_prop_cycle(None)
    for m in da.member.values[3:]:
        da.sel(member=m).plot(label=m, lw=1.5, ax=ax)
    #da.isel(member=slice(4,None)).plot(hue='member', lw=1, ax=ax)
    da.isel(member=0).plot(lw=3, color='k', ls='-', ax=ax, label='all sites')

    ax.legend(ncol=4, loc='upper left')
    title = ' '.join( os.path.splitext(ofile)[0].split('_') )
    ax.set_title(title)
    
    #savefig
    if len(sys.argv)>1 and 'savefig' in sys.argv[1:]:
        #figname = __file__.replace('.py', f'.png')
        figname = ofile.replace('.nc', '.png')
        if 'overwritefig' in sys.argv[1:]:
            wysavefig(figname, overwritefig=True)
        else:
            wysavefig(figname)
    tt.check(f'**Done**')
    plt.show()
    
