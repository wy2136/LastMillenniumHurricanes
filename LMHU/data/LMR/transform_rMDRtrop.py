#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Thu Sep  9 17:30:57 EDT 2021
if __name__ == '__main__':
    from misc.timer import Timer
    tt = Timer(f'start {__file__}')
import sys, os.path, os, glob, datetime
import xarray as xr, numpy as np, pandas as pd, matplotlib.pyplot as plt
#more imports
import xfilter
#
if __name__ == '__main__':
    tt.check('end import')
#
#start from here
yearsRef = slice(1870, 2000)
individualScale = False #whether to transform based on each ensemble member or the ensemble mean
ds_obs = xr.open_dataset('/tigress/wenchang/analysis/LMTC/data/HadISST/HadISST_sstmdrtrop_plusChanCorr.1870-2019.nc')
ds_lmr2018 = xr.open_dataset('LMR2018TC.nc')
ds_lmr2019 = xr.open_dataset('LMR2019TC.nc')
anomaly = lambda x: x - x.sel(year=slice(1982,2005)).mean()
lpwindow = 40
lowpass = lambda x: x.filter.lowpass(1/lpwindow, dim='year', padtype='even')
def transform(da, daname, yearsRef=None, individualScale=False):
    if yearsRef is None:
        yearsRef = slice(1901,2000)
    if individualScale: #transform for each ensemble member
        da_lp = da.pipe(lowpass)
    else: #transform the ensemble mean
        da_lp = da.pipe(lowpass).mean('MCrun')
    selfMean = da_lp.sel(year=yearsRef).mean('year')
    selfSTD = da_lp.sel(year=yearsRef).std('year')
    if daname == 'rMDR':
        da_target = (ds_obs['MDR'] - ds_obs['TROP']).pipe(anomaly).pipe(lowpass) 
    else:
        da_target = ds_obs[daname].pipe(anomaly).pipe(lowpass) 
    targetMean = da_target.sel(year=yearsRef).mean('year')
    targetSTD = da_target.sel(year=yearsRef).std('year')
    return (da - selfMean)*targetSTD/selfSTD + targetMean

#lmr2018
ofile = 'LMR2018_sstmdrtrop_rMDRtransformed.nc'
if yearsRef is not None:
    ofile = ofile.replace('.nc', f'{yearsRef.start}{yearsRef.stop}.nc')
if individualScale:
    ofile = ofile.replace('.nc', '_individualScale.nc')
if os.path.exists(ofile):
    print('[exists]:', ofile)
    ds_lmr2018tf = xr.open_dataset(ofile)
else:
    rMDR = (ds_lmr2018['MDR'] - ds_lmr2018['TROP']).pipe(transform, daname='rMDR', yearsRef=yearsRef, individualScale=individualScale)
    trop = ds_lmr2018['TROP'].pipe(transform, daname='TROP', yearsRef=yearsRef, individualScale=individualScale)
    mdr = trop + rMDR
    ds = xr.Dataset(dict(MDR=mdr, TROP=trop))
    ds.to_netcdf(ofile)
    print('[saved]:', ofile)
    ds_lmr2018tf = ds
#lmr2019
ofile = 'LMR2019_sstmdrtrop_rMDRtransformed.nc'
if yearsRef is not None:
    ofile = ofile.replace('.nc', f'{yearsRef.start}{yearsRef.stop}.nc')
if individualScale:
    ofile = ofile.replace('.nc', '_individualScale.nc')
if os.path.exists(ofile):
    print('[exists]:', ofile)
    ds_lmr2019tf = xr.open_dataset(ofile)
else:
    rMDR = (ds_lmr2019['MDR'] - ds_lmr2019['TROP']).pipe(transform, daname='rMDR', yearsRef=yearsRef, individualScale=individualScale)
    trop = ds_lmr2019['TROP'].pipe(transform, daname='TROP', yearsRef=yearsRef, individualScale=individualScale)
    mdr = trop + rMDR
    ds = xr.Dataset(dict(MDR=mdr, TROP=trop))
    ds.to_netcdf(ofile)
    print('[saved]:', ofile)
    ds_lmr2019tf = ds

 
if __name__ == '__main__':
    from wyconfig import * #my plot settings
    #plt.close()
    if 'TROP' in sys.argv:
        daname = 'TROP'
    elif 'rMDR' in sys.argv:
        daname = 'rMDR'
    else:
        daname = 'MDR'
    selyears = lambda x: x.sel(year=slice(850, None))
    alpha = 0.1
    fig, ax = plt.subplots()
    #lmr2018
    if daname == 'rMDR':
        da = ds_lmr2018['MDR'] - ds_lmr2018['TROP']
    else:
        da = ds_lmr2018[daname]
    da.pipe(anomaly).pipe(lowpass).pipe(selyears).plot(hue='MCrun', color='C0', alpha=alpha, add_legend=False, ax=ax)
    da.pipe(anomaly).pipe(lowpass).pipe(selyears).mean('MCrun').plot(color='C0', ax=ax, label='LMR2.0')
    #lmr2019
    if daname == 'rMDR':
        da = ds_lmr2019['MDR'] - ds_lmr2019['TROP']
    else:
        da = ds_lmr2019[daname]
    da.pipe(anomaly).pipe(lowpass).pipe(selyears).plot(hue='MCrun', color='C1', alpha=alpha, add_legend=False, ax=ax)
    da.pipe(anomaly).pipe(lowpass).pipe(selyears).mean('MCrun').plot(color='C1', ax=ax, label='LMR2.1')
    #obs
    if daname == 'rMDR':
        da = ds_obs['MDR'] - ds_obs['TROP']
    else:
        da = ds_obs[daname]
    da.pipe(anomaly).pipe(lowpass).plot(color='k', ax=ax, label='HadISSTchan')

    #lmr2018 transformed
    if daname == 'rMDR':
        da = ds_lmr2018tf['MDR'] - ds_lmr2018tf['TROP']
    else:
        da = ds_lmr2018tf[daname]
    da.pipe(lowpass).pipe(selyears) \
        .plot(hue='MCrun', color='C2', alpha=alpha, add_legend=False, ax=ax)
    da.pipe(lowpass).pipe(selyears) \
        .mean('MCrun') \
        .plot(color='C2', ls='--', ax=ax, label='LMR2.0 transformed')
    #lm2019 transformed
    if daname == 'rMDR':
        da = ds_lmr2019tf['MDR'] - ds_lmr2019tf['TROP']
    else:
        da = ds_lmr2019tf[daname]
    da.pipe(lowpass).pipe(selyears) \
        .plot(hue='MCrun', color='C3', alpha=alpha, add_legend=False, ax=ax)
    da.pipe(lowpass).pipe(selyears) \
        .mean('MCrun') \
        .plot(color='C3', ls='--', ax=ax, label='LMR2.1 transformed')


    ax.legend()
    ax.set_ylabel(f'{daname} [K]')
    ax.set_xlim(850, 2020)
    #ax.set_xticks(range(900, 2020, 100))
    #ax.set_ylim(-0.7, 0.4)
    
    #savefig
    if 'savefig' in sys.argv:
        figname = __file__.replace('.py', f'_{daname}.png')
        if yearsRef is not None:
            figname = figname.replace('.png', f'_tf{yearsRef.start}{yearsRef.stop}.png')
        if individualScale:
            figname = figname.replace('.png', '_individualScale.png')
        wysavefig(figname)
    tt.check(f'**Done**')
    plt.show()
    
