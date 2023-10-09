#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Sun Jan  9 23:28:32 EST 2022
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
daname = 'HU' #default daname
if len(sys.argv)>1:
    if 'rMDRa' in sys.argv[1:]:
        daname = 'rMDRa'
    elif 'TROPa' in sys.argv[1:]:
        daname = 'TROPa'

ifiles = """
LME_sstTC_fullForcing_13ens.nc
LME_sstTC_GHG_3ens.nc
LME_sstTC_VOLC_GRA_5ens.nc
LME_sstTC_LULC_HurttPongratz_3ens.nc
LME_sstTC_SSI_VSK_L_4ens.nc
LME_sstTC_ORBITAL_3ens.nc
LME_sstTC_OZONE_AER_3ens.nc
""".split()
cases = ['_'.join( f.split('_')[2:-1] ) for f in ifiles]
print(ifiles)
print(cases)
n_cases = len(cases)
ofile = f'LME_{daname}_{n_cases}cases_smooth{n_window}yr_ensmean.nc'
if os.path.exists(ofile):
    ds = xr.open_dataset(ofile)
    print('[loaded]:', ofile)
else:
    das = []
    ens_sizes = []
    for ifile in ifiles:
        if daname == 'rMDRa': 
            ds_ = xr.open_dataset(ifile)
            da = ds_['MDRa'] - ds_['TROPa']
        else:
            da = xr.open_dataset(ifile)[daname]
        ens_sizes.append(da.ens.size)
        das.append(da.mean('ens').pipe(lowpass)) #lowpass in the loop; otherwise the OZONE_AER case will become NaNs due to shorter time span
    da = xr.concat(das, dim=pd.Index(cases, name='case'))
    ens_sizes = xr.DataArray(ens_sizes, dims='case').assign_coords(case=cases)
    ds = xr.Dataset({daname: da, 'ens_size': ens_sizes})
    ds.to_netcdf(ofile)
    print('[saved]:', ofile)

 
 
if __name__ == '__main__':
    from wyconfig import * #my plot settings
    plt.close()
    figsize = (8,3)
    fig, ax = plt.subplots(figsize=figsize)
    case = 'fullForcing'
    label = f'{case}({ds.ens_size.sel(case=case).item()})'
    ds[daname].sel(case=case).plot(ax=ax, color='k', label=label, lw=2)
    ax.set_prop_cycle(None)
    for case in ds.case.values[1:]:
        label = f'{case}({ds.ens_size.sel(case=case).item()})'
        ds[daname].sel(case=case).plot(ax=ax, label=label, alpha=0.5)

    ax.legend(ncol=3)
    if daname == 'HU':
        ax.set_ylim(5,11)
    elif daname == 'rMDRa':
        ax.set_ylim(-0.01, 0.4)
    elif daname == 'TROPa':
        ax.set_ylim(-0.7, 0.7)
    ax.set_xlim(850,2000)
    ax.set_xticks(range(2000,850,-100))
    ax.set_title('')
    if daname in ('HU', 'MH'):
        ax.set_ylabel(f'LME {daname} count')
    elif daname in ('rMDRa', ):
        ax.set_ylabel(f'LME MDR$-$TROP SST anom [K]')
    elif daname in ('TROPa', ):
        ax.set_ylabel(f'LME TROP SST anom [K]')
        
    
    #savefig
    if len(sys.argv)>1 and 'savefig' in sys.argv[1:]:
        #figname = __file__.replace('.py', f'.png')
        figname = ofile.replace('.nc', f'.png')
        if 'overwritefig' in sys.argv[1:]:
            wysavefig(figname, overwritefig=True)
        else:
            wysavefig(figname)
    tt.check(f'**Done**')
    plt.show()
    
