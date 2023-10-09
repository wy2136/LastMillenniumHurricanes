#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Thu Jan 27 14:25:41 EST 2022
if __name__ == '__main__':
    import sys
    from misc.timer import Timer
    tt = Timer('start ' + ' '.join(sys.argv))
import sys, os.path, os, glob, datetime
import xarray as xr, numpy as np, pandas as pd, matplotlib.pyplot as plt
#more imports
import cartopy.crs as ccrs, cartopy.feature as cfeature
from shared import axlabel
#
if __name__ == '__main__':
    tt.check('end import')
#
#start from here
ifile = 'data/LME/linregress_map/linregress_map_lmeSST_HU_850-1850_fullForcing.nc'
ds_full = xr.open_dataset(ifile)
ifile = 'data/LME/linregress_map/linregress_map_lmeSST_HU_850-1850_VOLC_GRA.nc'
ds_volc = xr.open_dataset(ifile)
ifile = 'data/LME/linregress_map/linregress_map_lmeSST_HU_850-1850_0850cntl.nc'
ds_cntl = xr.open_dataset(ifile)
p_alpha = 0.1

def wyplot(ds, show_slope=False, ax=None, **kws):
    if ax is None: fig, ax = plt.subplots(subplot_kw=dict(projection=ccrs.Robinson(central_longitude=180)))
    dproj = ccrs.PlateCarree()
    land_color = 'k'
    if show_slope:
        da = ds.slope.assign_attrs(long_name='slope')
        levels = np.arange(-0.12, 0.121, 0.02)
        extend = 'both'
    else:
        da = ds.r
        levels = np.arange(-1, 1.01, 0.1)
        extend = 'neither'
    p = ds.pvalue
    da.plot.contourf(ax=ax, transform=dproj, levels=levels, extend=extend, **kws)
    #mapplot(ax=ax, fill_continents=True)
    da.where(p<p_alpha).plot.contourf(ax=ax, transform=dproj, colors='none', hatches=['...'], add_colorbar=False)

    ax.add_feature(cfeature.LAND, color=land_color)
    ax.set_global()
    #ax.gridlines()

 
if __name__ == '__main__':
    from wyconfig import * #my plot settings
    proj = ccrs.Robinson(central_longitude=180)
    dproj = ccrs.PlateCarree()
    fig, axes = plt.subplots(3, 2, figsize=(8.8, 6), subplot_kw=dict(projection=proj))
    ax = axes[0,0]
    wyplot(ds_full, ax=ax, show_slope=False)
    ax = axes[0,1]
    wyplot(ds_full, ax=ax, show_slope=True)
    ax = axes[1,0]
    wyplot(ds_volc, ax=ax, show_slope=False)
    ax = axes[1,1]
    wyplot(ds_volc, ax=ax, show_slope=True)
    ax = axes[2,0]
    wyplot(ds_cntl, ax=ax, show_slope=False)
    ax = axes[2,1]
    wyplot(ds_cntl, ax=ax, show_slope=True)

    for ax in axes.flat:#[2:]:
        ax.set_title('')
    for ax,ylabel in zip(axes.flat[0::2], ['Full Forcing', 'VOLC_GRA', '0850cntl']):
        ax.text(0-0.05, 0.5, ylabel, transform=ax.transAxes, va='center', ha='center', rotation=90)
    for ax,label in zip(axes.flat, list('abcdef'.upper())):
        axlabel(ax, label)
    
    #savefig
    if len(sys.argv)>1 and 'savefig' in sys.argv[1:]:
        figname = __file__.replace('.py', f'.png')
        if p_alpha != 0.05: figname = figname.replace('.png', f'_alpha{int(p_alpha*100)}.png')
        if 'overwritefig' in sys.argv[1:]:
            wysavefig(figname, overwritefig=True)
        else:
            wysavefig(figname)
    tt.check(f'**Done**')
    print()
    plt.show()
    
