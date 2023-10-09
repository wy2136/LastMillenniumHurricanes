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
pyleoclim = True if len(sys.argv)>1 and 'pyleoclim' in sys.argv[1:] else False
rSST = True if len(sys.argv)>1 and 'rSST' in sys.argv[1:] else False
#params for figure
show_slope = True if len(sys.argv)>1 and 'slope' in sys.argv[1:] else False #whether to plot slope of regression or corrcoef

daname = 'sst'
n_window = (500, 40)
bandpass = lambda da: da.filter.bandpass((1/n_window[0], 1/n_window[1]), dim='year', padtype='even')
years = slice(201,2000)
ifile_sst = '/tigress/wenchang/MODEL_OUT/CTL1860_newdiag_tigercpu_intelmpi_18_576PE/analysis/sst.0001-2000.yearly.nc'
ifile_tc = '/tigress/wenchang/analysis/TC/CTL1860_newdiag_tigercpu_intelmpi_18_576PE/netcdf/tc_counts.TS17.0001-2000.yearly.nc'

ofile = f'linregress_map_FLOR_SST_TC_{years.start}-{years.stop}.nc'
if pyleoclim:
    ofile = ofile.replace('.nc', '_pyleoclim.nc')
if rSST:
    ofile = ofile.replace('SST', 'rSST')

if os.path.exists(ofile):
    ds = xr.open_dataset(ofile)
    print('[loaded]:', ofile)
else:
    #TC
    print('FLOR TC...')
    da = xr.open_dataset(ifile_tc)['NA'].pipe(bandpass).sel(year=years)
    da_tc = ( da - da.mean() )/da.std() #standardize
    #SST
    print('FLOR SST...')
    da = xr.open_dataset(ifile_sst)['sst']
    if rSST:
        #relative SST: subtract tropical mean
        weights = np.cos( np.deg2rad(da.lat) )
        da = da - da.sel(lat=slice(-30, 30)).weighted(weights).mean(['lat', 'lon'])
    #da = ds_lmr[daname].groupby('time.year').mean('time').load()
    da_sst = da.pipe(bandpass).sel(year=years)
    if pyleoclim:
        result = xpyleoclim.correlation(da_sst, da_tc, seed=0)
        ds = result[['r', 'p', 'signif']].rename(p='pvalue')
        slope = ds['r'] * da_sst.std('year')/da_tc.std('year')
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
    else:
        da = ds.r
        levels = np.arange(-1, 1.01, 0.1)
    p = ds.pvalue
    da.plot.contourf(ax=ax, transform=dproj, levels=levels, **kws)
    #mapplot(ax=ax, fill_continents=True)
    da.where(p<0.05).plot.contourf(ax=ax, transform=dproj, colors='none', hatches=['...'], add_colorbar=False)

    ax.add_feature(cfeature.LAND, color=land_color)
    ax.set_global()
    #ax.gridlines()
    
    if show_slope:
        title = f'linear regression of FLOR SST onto HU'
    else:
        title = f'corr coef between FLOR SST and HU'
    if rSST:
        title = title.replace('SST', 'rSST')
    if pyleoclim:
        title += ', pyleoclim'
    ax.set_title(title) 

if __name__ == '__main__':
    from wyconfig import * #my plot settings
    from geoplots import mapplot
    import cartopy.crs as ccrs, cartopy.feature as cfeature
    plt.close()
    proj = ccrs.Robinson(central_longitude=180)
    #proj = ccrs.Mollweide(central_longitude=180)
    dproj = ccrs.PlateCarree()
    figsize = (6,3)
    fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(projection=proj))
    wyplot(ds, show_slope=show_slope, ax=ax)

    """
    figsize = (6,6)
    fig, axes = plt.subplots(2, 1, figsize=figsize, subplot_kw=dict(projection=proj))

    ax = axes[0]
    wyplot(ds, show_slope=False, ax=ax)

    ax= axes[1]
    wyplot(ds, show_slope=True, ax=ax)
    """

    #savefig
    if len(sys.argv)>1 and 'savefig' in sys.argv[1:]:
        #figname = __file__.replace('.py', f'.png')
        if show_slope:
            figname = ofile.replace('.nc', '_slope.png')
        else:
            figname = ofile.replace('.nc', '_corr.png')
        if 'overwritefig' in sys.argv[1:]:
            wysavefig(figname, overwritefig=True)
        else:
            wysavefig(figname)
    tt.check(f'**Done**')
    plt.show()
    
