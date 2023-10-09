#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Mon Feb  8 22:29:10 EST 2021
if __name__ == '__main__':
    from misc.timer import Timer
    tt = Timer(f'start {__file__}')
import sys, os.path, os, glob, datetime
import xarray as xr, numpy as np, pandas as pd
import matplotlib.pyplot as plt
#more imports
from geoplots.cartopy.api import cartoplot
import geoxarray
#
if __name__ == '__main__':
    tt.check('end import')
#
#start from here
#data
#LME
yearc = 1277 # center year
n_window = 40
yearsRef = slice(850,1850)
rSST = False
daname = 'ssta'
long_name = 'SST anom'
units = 'K'

if len(sys.argv)>1:
    if '1980' in sys.argv:
        yearc = 1980
    if 'rSST' in sys.argv:
        rSST = True
years = slice(yearc-n_window//2, yearc+n_window//2)
tag = f'{years.start}-{years.stop}_ref{yearsRef.start}-{yearsRef.stop}'
if rSST:
    tag += '_rSST'
    long_name = long_name.replace('SST', 'rSST')

ofile = __file__.replace('.py', f'_{tag}.nc')
if os.path.exists(ofile):
    da = xr.open_dataarray(ofile)
else:
    #ifile = '/tigress/gvecchi/DATA/LMR_2019/sst_MCruns_ensemble_mean.nc'
    ifile = '/tigress/wenchang/analysis/LMTC/data/b.e11.BLMTRC5CN.f19_g16.001-013.cam.h0.TS.0850-2005.nc'
    print(ifile, 'loading...')
    da = xr.open_dataarray(ifile).load()
    da = da.mean('en') \
        .pipe(lambda x: x.sel(year=years).mean('year') - x.sel(year=yearsRef).mean('year'))
    if rSST:
        da = da - da.sel(lat=slice(-30,30)).geo.fldmean()
    da = da.assign_attrs(units=units, long_name=long_name)
    da.to_dataset(name=daname).to_netcdf(ofile)
    print('[saved]:', ofile)

def wyplot(ax=None, **kws):
    if ax is None:
        fig, ax = plt.subplots()
    da.plot.contourf(cmap='RdBu_r', extend='both', **kws)
    plt.title(f'LME {years.start}-{years.stop} minus {yearsRef.start}-{yearsRef.stop}')
    
 
if __name__ == '__main__':
    from wyconfig import * #my plot settings
    import cartopy.crs as ccrs, cartopy.feature as cfeature
    proj = ccrs.Robinson(central_longitude=180)
    dproj = ccrs.PlateCarree()
    land_color = 'k'
    figsize = (9,4)
    #fig, axes = plt.subplots(2, 2, figsize=figsize, subplot_kw=dict(projection=proj))
    fig, ax = plt.subplots(subplot_kw=dict(projection=proj))
    vmax = 1 if yearc==1980 else 0.32
    levels = 21 if yearc==1980 else 17
    wyplot(ax=ax, transform=dproj, vmax=vmax, levels=levels)
    ax.add_feature(cfeature.LAND, color=land_color)
    
    figname = __file__.replace('.py', f'_{tag}.png')
    if len(sys.argv) > 1 and 'savefig' in sys.argv:
        wysavefig(figname)
    tt.check(f'**Done**')
    plt.show()
    
