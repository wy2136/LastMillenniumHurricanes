#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Thu Apr 14 13:29:30 EDT 2022
if __name__ == '__main__':
    import sys
    from misc.timer import Timer
    tt = Timer('start ' + ' '.join(sys.argv))
import sys, os.path, os, glob, datetime
import xarray as xr, numpy as np, pandas as pd, matplotlib.pyplot as plt
#more imports
from misc.shell import run_shell
#
if __name__ == '__main__':
    tt.check('end import')
#
#start from here
def wyplot(yearc, rSST=False, ax=None, **kws):
    if ax is None:
        fig, ax = plt.subplots()
    #yearc = 1420
    n_window = 40
    #rSST = False
    years = slice(yearc-n_window//2, yearc+n_window//2)
    ifile = f'./data/maps_ssta/map_ssta_LMR2019_{years.start}-{years.stop}_ref850-1850.nc'
    if rSST:
        ifile = ifile.replace('.nc', '_rSST.nc')
    #print(f'{ifile = }')
    #da = xr.open_dataarray(ifile)
    ifile_cached = __file__.replace('.py', f'__{years.start:04d}-{years.stop:04d}.nc')
    if rSST: ifile_cached = ifile_cached.replace('.nc', '_rSST.nc')
    if not os.path.exists(ifile_cached): run_shell(f'cp {ifile} {ifile_cached}')
    da = xr.open_dataarray(ifile_cached)
    print('[loaded]:', ifile_cached, '**from**', ifile)
    
    da.plot.contourf(ax=ax, levels=17, cmap='RdBu_r', extend='neither', **kws)
    ax.set_title(f'LMR2.1 {years.start}-{years.stop} minus 850-1850')
 
 
if __name__ == '__main__':
    from wyconfig import * #my plot settings
    import cartopy.crs as ccrs, cartopy.feature as cfeature
    proj = ccrs.Robinson(central_longitude=180)
    dproj = ccrs.PlateCarree()
    land_color = 'k'
    figsize = (9,4)
    fig, axes = plt.subplots(2, 2, figsize=figsize, subplot_kw=dict(projection=proj))
    ax = axes[0,0]
    wyplot(1420, ax=ax, transform=dproj, vmax=0.32)
    ax.add_feature(cfeature.LAND, color=land_color)

    ax = axes[0,1]
    wyplot(1420, rSST=True, ax=ax, transform=dproj, vmax=0.32)
    ax.add_feature(cfeature.LAND, color=land_color)

    ax = axes[1,0]
    wyplot(1726, ax=ax, transform=dproj, vmax=0.32)
    ax.add_feature(cfeature.LAND, color=land_color)

    ax = axes[1,1]
    wyplot(1726, rSST=True, ax=ax, transform=dproj, vmax=0.32)
    ax.add_feature(cfeature.LAND, color=land_color)
    
    #savefig
    if len(sys.argv)>1 and 'savefig' in sys.argv[1:]:
        figname = __file__.replace('.py', f'.png')
        if 'overwritefig' in sys.argv[1:]:
            wysavefig(figname, overwritefig=True)
        else:
            wysavefig(figname)
    tt.check(f'**Done**')
    print()
    plt.show()
    
