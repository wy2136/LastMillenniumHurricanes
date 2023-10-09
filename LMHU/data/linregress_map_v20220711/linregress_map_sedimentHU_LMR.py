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
lmr = 2018 if len(sys.argv)>1 and '2018' in sys.argv[1:] else 2019
pyleoclim = True if len(sys.argv)>1 and 'pyleoclim' in sys.argv[1:] else False
rSST = True if len(sys.argv)>1 and 'rSST' in sys.argv[1:] else False
case = 'noCaySal'
if len(sys.argv)>1:
    if 'noCaySal_noCaicos' in sys.argv[1:]:
        case = 'noCaySal_noCaicos'
    if 'wCaySal' in sys.argv[1:]:
        case = 'wCaySal'
siglev = 0.1 #usually 0.05

daname = 'sst'
n_window = 40
lowpass = lambda da: da.filter.lowpass(1/n_window, dim='year', padtype='even')
years = slice(850,1850)
assert lmr == 2019 or lmr == 2018, 'lmr can only be 2019 or 2018'
if lmr == 2019:
    lmr_version = '2.1'
elif lmr == 2018:
    lmr_version == '2.0'

ofile = f'linregress_map_sedimentHU{case}_on_LMR{lmr}SST_{years.start}-{years.stop}.nc'
if pyleoclim:
    ofile = ofile.replace('.nc', '_pyleoclim.nc')
if rSST:
    ofile = ofile.replace('SST', 'rSST')

if os.path.exists(ofile):
    ds = xr.open_dataset(ofile)
    print('[loaded]:', ofile)
else:
    #ds_liz = xr.open_dataset(f'../Lizzie/sedimentHU_v20220121_{case}_smooth40yr_count.nc')
    ds_liz = xr.open_dataset(f'../Lizzie/sedimentHU_v20220711ens_{case}_wy_max_lp40_count.nc')
    if lmr == 2018:
        ds_lmr = xr.open_dataset('/tigress/gvecchi/DATA/LMR_2018/sst_MCruns_ensemble_mean.nc')
    elif lmr == 2019:
        ds_lmr = xr.open_dataset('/tigress/gvecchi/DATA/LMR_2019/sst_MCruns_ensemble_mean.nc')
    #sediment HU
    print('sediment HU...')
    da_liz = ds_liz['sedimentHUcount'].sel(member='sediment_estimate').sel(year=years)
    da_liz = ( da_liz - da_liz.mean() )/da_liz.std() #standardize
    #LMR SST
    print('LMR SST...')
    da = ds_lmr[daname]
    da = da.assign_coords(time=da.time.dt.year.values).rename(time='year')
    if rSST:
        #relative SST: subtract tropical mean
        weights = np.cos( np.deg2rad(da.lat) )
        da = da - da.sel(lat=slice(-30, 30)).weighted(weights).mean(['lat', 'lon'])
    #da = ds_lmr[daname].groupby('time.year').mean('time').load()
    da_lmr = da.mean('MCrun').pipe(lowpass).sel(year=years)
    if pyleoclim:
        result = xpyleoclim.correlation(da_lmr, da_liz, seed=0)
        ds = result[['r', 'p', 'signif']].rename(p='pvalue')
        slope = ds['r'] * da_lmr.std('year')/da_liz.std('year')
        ds['slope'] = slope.assign_attrs(units='K per STD HU')
    else:
        print('linear regression...')
        rg = da_lmr.linregress.on(da_liz, dim='year', ess_on=True)
        ds = rg[['slope', 'r', 'dof', 'pvalue']]
        ds['slope'].attrs['units'] = 'K per STD HU'
    ds.to_netcdf(ofile)
    print('[saved]:', ofile)
 
def wyplot(ds, slope=False, ax=None, **kws):
    if ax is None: fig, ax = plt.subplots(subplot_kw=dict(projection=ccrs.Robinson(central_longitude=180)))
    dproj = ccrs.PlateCarree()
    land_color = 'k'
    if slope:
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
    da.where(p<siglev).plot.contourf(ax=ax, transform=dproj, colors='none', hatches=['...'], add_colorbar=False)

    ax.add_feature(cfeature.LAND, color=land_color)
    ax.set_global()
    #ax.gridlines()
    
    if slope:
        title = f'LMR{lmr_version}SST on sediment HU {case}'
    else:
        title = f'LMR{lmr_version}SST and sediment HU {case}'
    if rSST:
        title = title.replace('SST', 'rSST')
    if pyleoclim:
        title += '; pyleoclim'
    if siglev > 0.05:
        title += f'; alpha={siglev}'
    ax.set_title('')
    ax.set_title(title, loc='left') 

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
    wyplot(ds, slope=False, ax=ax)

    ax= axes[1]
    wyplot(ds, slope=True, ax=ax)

    #savefig
    if len(sys.argv)>1 and 'savefig' in sys.argv[1:]:
        #figname = __file__.replace('.py', f'.png')
        figname = ofile.replace('.nc', '.png')
        if siglev > 0.05:
            figname = figname.replace('.png', f'_alpha{int(siglev*100)}.png')
        if 'overwritefig' in sys.argv[1:]:
            wysavefig(figname, overwritefig=True)
        else:
            wysavefig(figname)
    tt.check(f'**Done**')
    plt.show()
    
