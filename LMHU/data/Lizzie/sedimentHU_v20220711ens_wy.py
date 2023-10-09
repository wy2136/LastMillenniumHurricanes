#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Wed Jul 20 12:17:20 EDT 2022
# use sedimentHU_v20220711ens_noCaySal.nc to get final TC activity
if __name__ == '__main__':
    import sys
    from misc.timer import Timer
    tt = Timer('start ' + ' '.join(sys.argv))
import sys, os.path, os, glob, datetime
import xarray as xr, numpy as np, pandas as pd, matplotlib.pyplot as plt
#more imports
import xfilter
nwindow = 40
lowpass = lambda x: x.filter.lowpass(1/nwindow, dim='year', padtype='even')
#
if __name__ == '__main__':
    tt.check('end import')
#
#start from here
ifile = 'sedimentHU_v20220711ens_noCaySal.nc'
if 'wCaySal' in sys.argv:
    ifile = ifile.replace('noCaySal', 'wCaySal')
method = 'max' #default is max across Monte Carlo members, same as Mann et al. 2009.
if 'median' in sys.argv:
    method = 'median'
elif 'mean' in sys.argv:
    method = 'mean'
age_error_in = False
if 'age_error' in sys.argv:
    age_error_in = True
ofile = __file__.replace('_wy.py', f'_noCaySal_wy_{method}_lp{nwindow}.nc')
ofile = os.path.basename(ofile)
if 'wCaySal' in sys.argv:
    ofile = ofile.replace('noCaySal', 'wCaySal')
if age_error_in:
    ofile = ofile.replace('.nc', '_ageerr.nc')

if os.path.exists(ofile):
    da = xr.open_dataarray(ofile)
    print('[loaded]:', ofile)
    #print('[exists]:', ofile)
    #sys.exit()
else:
    da = xr.open_dataarray(ifile)
    
    #uncertainty from bootstrap of 2000 MC members max/median due to age error
    if age_error_in:
        zz = da.sel(jk='allSites').transpose('mc', 'year').values
        rng = np.random.default_rng(20220721)
        nbs, nmc = 1000, da.mc.size #bootstrap sample size = 1000
        zz = zz[rng.choice(nmc, size=(nbs,nmc)), :] #TODO
        da_bs = xr.DataArray(zz, dims=('bs','mc','year')).assign_coords(year=da.year.values)
        if method == 'median':
            ee = da_bs.median('mc').pipe(lowpass).std('bs') * 2
        elif method == 'mean':
            ee = da_bs.mean('mc').pipe(lowpass).std('bs') * 2
        else:
            ee = da_bs.max('mc').pipe(lowpass).std('bs') * 2
        ee_bs = ee
    else:
        ee_bs = 0
    
    #estimate
    if method == 'median':
        da = da.median('mc').pipe(lowpass)
    elif method == 'mean':
        da = da.mean('mc').pipe(lowpass)
    else:
        da = da.max('mc').pipe(lowpass)
    
    
    #uncertainty from jackknife resampling
    ee = da.isel(jk=slice(1,None)).std('jk') * 2#all jackknife members (exclude allSites); 2xSTD
    ee = np.sqrt(ee**2 + ee_bs**2) #merge age error in 
    sediment_estimate = da.sel(jk=['allSites',]).assign_coords(jk=['sediment_estimate'])
    lower_estimate = (sediment_estimate - ee).assign_coords(jk=['lower_estimate'])
    upper_estimate = (sediment_estimate + ee).assign_coords(jk=['upper_estimate'])
    
    #merge
    da = xr.concat([sediment_estimate, lower_estimate, upper_estimate, da.isel(jk=slice(1, None))], dim='jk')
    da = da.rename(jk='member')
    
    #save
    da.to_dataset(name='sedimentHU').to_netcdf(ofile)
    print('[saved]:', ofile)

 
 
if __name__ == '__main__':
    from wyconfig import * #my plot settings
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
    print()
    if 'notshowfig' in sys.argv:
        pass
    else:
        plt.show()
    
