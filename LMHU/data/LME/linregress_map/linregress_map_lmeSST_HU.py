#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Fri Dec 31 12:49:58 EST 2021
if __name__ == '__main__':
    import sys
    from misc.timer import Timer
    s = ' '
    tt = Timer(f'start {s.join(sys.argv)}')
import sys, os.path, os, glob, datetime
import xarray as xr, numpy as np, pandas as pd, matplotlib.pyplot as plt
#more imports
import xlinregress
import xfilter
import xpyleoclim
import cartopy.crs as ccrs, cartopy.feature as cfeature
#
if __name__ == '__main__':
    tt.check('end import')
#
#start from here
#params from sys.argv
case = 'fullForcing'
if len(sys.argv)>1:
    if 'VOLC_GRA' in sys.argv[1:]:
        case = 'VOLC_GRA'
    elif '0850cntl' in sys.argv[1:]:
        case = '0850cntl'
rSST = True if len(sys.argv)>1 and 'rSST' in sys.argv[1:] else False
pyleoclim = True if len(sys.argv)>1 and 'pyleoclim' in sys.argv[1:] else False
daname = 'MH' if len(sys.argv)>1 and 'MH' in sys.argv[1:] else 'HU'

n_window = 40
lowpass = lambda da: da.filter.lowpass(1/n_window, dim='year', padtype='even')
years = slice(850,1850)

ofile = f'linregress_map_lmeSST_HU_{years.start}-{years.stop}_{case}.nc'
if pyleoclim:
    ofile = ofile.replace('.nc', '_pyleoclim.nc')
if rSST:
    ofile = ofile.replace('lmeSST', 'LMErSST')

if os.path.exists(ofile):
    ds = xr.open_dataset(ofile)
    print('[loaded]:', ofile)
else:
    #LME HU
    print(f'LME {daname}...')
    if case in ('0850cntl',):
        da = xr.open_dataset(f'../LME/LME_sstTC_0850cntl.nc')[daname]
        da = da.pipe(lowpass).sel(year=years)
    else: #fullForcing or partialForcing cases
        da = xr.open_dataset(f'../LME/LME_{daname}_7cases_smooth40yr_ensmean.nc')[daname]
        da = da.sel(case=case).sel(year=years)
    da_tc = (da - da.mean('year'))/da.std('year')
    #LME SST
    print('LME SST...')
    ifile = '/tigress/wenchang/analysis/LMTC/data/b.e11.BLMTRC5CN.f19_g16.001-013.cam.h0.TS.0850-2005.nc' #default is the fullForcing case
    if case == 'VOLC_GRA':
        ifile = '/tigress/wenchang/analysis/LMTC/data/b.e11.BLMTRC5CN.f19_g16.VOLC_GRA.001-005.cam.h0.TS.0850-2005.nc'
    elif case == '0850cntl':
        ifile = '/tigress/wenchang/analysis/LMTC/data/b.e11.B1850C5CN.f19_g16.0850cntl.001.cam.h0.TS.0850-2005.nc'
    da = xr.open_dataarray(ifile)
    if rSST:
        #relative SST: subtract tropical mean
        weights = np.cos( np.deg2rad(da.lat) )
        da = da - da.sel(lat=slice(-30, 30)).weighted(weights).mean(['lat', 'lon'])
    if case in ('0850cntl',):
        da_sst = da.pipe(lowpass).sel(year=years)
    else:
        da_sst = da.mean('en').pipe(lowpass).sel(year=years)
    if pyleoclim:
        result = xpyleoclim.correlation(da_sst, da_tc, seed=0)
        ds = result[['r', 'p', 'signif']].rename(p='pvalue')
        slope = ds['r'] * da_lmr.std('year')/da_liz.std('year')
        ds['slope'] = slope.assign_attrs(units='K per STD HU')
    else:
        print('linear regression...')
        rg = da_sst.linregress.on(da_tc, dim='year', ess_on=True)
        ds = rg[['slope', 'r', 'dof', 'pvalue']]
        ds['slope'].attrs['units'] = 'K per STD HU'
    ds.to_netcdf(ofile)
    print('[saved]:', ofile)
 
def wyplot(ds, show_slope=False, ax=None, **kws):
    if ax is None: fig, ax = plt.subplots(subplot_kw=dict(projection=ccrs.Robinson(central_longitude=180)))
    dproj = ccrs.PlateCarree()
    land_color = 'k'
    if show_slope:
        da = ds.slope
        levels = np.arange(-0.12, 0.121, 0.02)
        extend = 'both'
    else:
        da = ds.r
        levels = np.arange(-1, 1.01, 0.1)
        extend = 'neither'
    p = ds.pvalue
    da.plot.contourf(ax=ax, transform=dproj, levels=levels, extend=extend, **kws)
    #mapplot(ax=ax, fill_continents=True)
    da.where(p<0.05).plot.contourf(ax=ax, transform=dproj, colors='none', hatches=['...'], add_colorbar=False)

    ax.add_feature(cfeature.LAND, color=land_color)
    ax.set_global()
    #ax.gridlines()
    
    if show_slope:
        title = f'linear regression of {case} LME SST on {daname}'
    else:
        title = f'corr coef between {case} LME SST and {daname}'
    if rSST:
        title = title.replace('SST', 'rSST')
    ax.set_title(title) 

if __name__ == '__main__':
    from wyconfig import * #my plot settings
    from geoplots import mapplot
    import cartopy.crs as ccrs, cartopy.feature as cfeature
    plt.close()
    figsize = (6,6)
    proj = ccrs.Robinson(central_longitude=180)
    #proj = ccrs.Mollweide(central_longitude=180)
    dproj = ccrs.PlateCarree()
    fig, axes = plt.subplots(2, 1, figsize=figsize, subplot_kw=dict(projection=proj))
    land_color = 'k'

    ax = axes[0]
    wyplot(ds, show_slope=False, ax=ax)

    ax= axes[1]
    wyplot(ds, show_slope=True, ax=ax)

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
    plt.show()
    
