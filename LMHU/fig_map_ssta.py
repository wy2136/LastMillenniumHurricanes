#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Wed Jan  4 14:00:48 EST 2023
if __name__ == '__main__':
    import sys
    from misc.timer import Timer
    tt = Timer('start ' + ' '.join(sys.argv))
import sys, os.path, os, glob, datetime
import xarray as xr, numpy as np, pandas as pd, matplotlib.pyplot as plt
#more imports
import cartopy.crs as ccrs, cartopy.feature as cfeature
from misc.shell import run_shell
#
if __name__ == '__main__':
    tt.check('end import')
#
#start from here
def wyplot(ax=None, lmr='2019', **kws): 
    #data
    ifile = f'./data/LMR/LMR{lmr}_ssta_0850-1850_ref1901-2000.nc'
    if lmr == '2018':
        lmr_version = '2.0'
    elif lmr == '2019':
        lmr_version = '2.1'
    else:
        print('lmr must be either 2019 or 2018')
        return
    long_name = f'LMR{lmr_version} SSTA: 0850-1850 minus 1901-2000'
    #da = xr.open_dataarray(ifile).load()
    #cache the data to current dir
    ifile_cached = __file__.replace('.py', f'__LMR{lmr}.nc')
    if not os.path.exists(ifile_cached) or 'od' in sys.argv: run_shell(f'cp {ifile} {ifile_cached}')
    da = xr.open_dataarray(ifile_cached).load()
    print('[loaded]:', ifile_cached)

    #plot
    proj = ccrs.Robinson(central_longitude=180)
    dproj = ccrs.PlateCarree()
    if ax is None:
        fig, ax = plt.subplots(subplot_kw=dict(projection=proj))
    land_color = 'k'
    levels = np.arange(-0.8, 0.801, 0.1)

    im = da.plot.contourf(ax=ax, transform=dproj, levels=levels, **kws)
    
    #MDR
    mdr_color = 'gray'
    latmin, latmax, lonmin, lonmax = 10, 25, 280, 340
    ax.plot([lonmin, lonmax, lonmax, lonmin, lonmin], [latmin, latmin, latmax, latmax, latmin], transform=dproj, color=mdr_color)
    lat0, lon0 = (latmin+latmax)/2, (lonmin+lonmax)/2
    ax.text(lon0, lat0, 'MDR', ha='center', va='center', transform=dproj, color=mdr_color)
    #trop
    latmin, latmax, lonmin, lonmax = -30, 30, 0, 360
    ax.plot([lonmin, lonmax, lonmax, lonmin, lonmin], [latmin, latmin, latmax, latmax, latmin], transform=dproj, color='gray', ls='--')

    ax.add_feature(cfeature.LAND, color=land_color)
    ax.set_title(long_name, loc='center')

    return im
    
 
if __name__ == '__main__':
    from wyconfig import * #my plot settings
    figsize = (8, 3*1.1)
    fig, axes = plt.subplots(1, 2, figsize=figsize, subplot_kw=dict(projection=ccrs.Robinson(central_longitude=180)))
    ax = axes[0]
    im = wyplot(ax=ax, lmr='2018', add_colorbar=False)
    ax = axes[1]
    im = wyplot(ax=ax, lmr='2019', add_colorbar=False)

    fig.colorbar(im, ax=axes, orientation='horizontal', label='K', shrink=0.5)

    #savefig
    if 'savefig' in sys.argv or 's' in sys.argv:
        figname = __file__.replace('.py', f'.png')
        if 'overwritefig' in sys.argv or 'o' in sys.argv:
            wysavefig(figname, overwritefig=True)
        else:
            wysavefig(figname)
    tt.check(f'**Done**')
    print()
    if 'notshowfig' in sys.argv:
        pass
    else:
        plt.show()
    
