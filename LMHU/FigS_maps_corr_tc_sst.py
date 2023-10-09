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
import cartopy.crs as ccrs, cartopy.feature as cfeature
from misc.shell import run_shell
#
if __name__ == '__main__':
    tt.check('end import')
#
#start from here
#params from sys.argv
lmr = 2018 if len(sys.argv)>1 and '2018' in sys.argv[1:] else 2019
pyleoclim = True if len(sys.argv)>1 and 'pyleoclim' in sys.argv[1:] else False
rSST = True if len(sys.argv)>1 and 'rSST' in sys.argv[1:] else False
assert lmr == 2019 or lmr == 2018, 'lmr can only be 2019 or 2018'
if lmr == 2019:
    lmr_version = '2.1'
elif lmr == 2018:
    lmr_version == '2.0'

#data
#LMR
years = slice(850,1850)
#ifile = f'data/linregress_map_v20201219/linregress_map_sedimentHU_on_LMR{lmr}SST_{years.start}-{years.stop}.nc'
#ifile = f'data/linregress_map/linregress_map_sedimentHUnoCaySal_on_LMR{lmr}SST_{years.start}-{years.stop}.nc'
ifile = f'data/linregress_map_v20220711/linregress_map_sedimentHUnoCaySal_on_LMR{lmr}SST_{years.start}-{years.stop}.nc'
ifile_cached = __file__.replace('.py', f'__LMR{lmr}SST.nc')
if pyleoclim:
    ifile = ifile.replace('.nc', '_pyleoclim.nc')
    ifile_cached = ifile_cached.replace('.nc', '_pyleoclim.nc')
if rSST:
    ifile = ifile.replace('SST', 'rSST')
    ifile_cached = ifile_cached.replace('SST', 'rSST')
#ds_lmr = xr.open_dataset(ifile)
#print('[loaded]:', ifile)
if not os.path.exists(ifile_cached): run_shell(f'cp {ifile} {ifile_cached}')
ds_lmr = xr.open_dataset(ifile_cached)
print('[loaded]:', ifile_cached, 'from', ifile)



#FLOR
years = slice(201,2000)
ifile = f'data/FLOR/linregress_map_FLOR_SST_TC_{years.start}-{years.stop}.nc'
ifile_cached = __file__.replace('.py', f'__FLORSST.nc')
if pyleoclim:
    ifile = ifile.replace('.nc', '_pyleoclim.nc')
    ifile_cached = ifile_cached.replace('.nc', '_pyleoclim.nc')
if rSST:
    ifile = ifile.replace('SST', 'rSST')
    ifile_cached = ifile_cached.replace('SST', 'rSST')
#ds_flor = xr.open_dataset(ifile)
#print('[loaded]:', ifile)
if not os.path.exists(ifile_cached): run_shell(f'cp {ifile} {ifile_cached}')
ds_flor = xr.open_dataset(ifile_cached)
print('[loaded]:', ifile_cached, 'from', ifile)
 
def wyplot(ds, slope=False, ax=None, flor=False, p_alpha=0.05, **kws):
    if ax is None: fig, ax = plt.subplots(subplot_kw=dict(projection=ccrs.Robinson(central_longitude=180)))
    dproj = ccrs.PlateCarree()
    land_color = 'k'
    if slope:
        da = ds.slope
        levels = np.arange(-0.12, 0.121, 0.02)
        da = da.assign_attrs(units='K per STD of HU', long_name='slope')
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
    
    if slope:
        title = f'LMR{lmr_version} SST regressed on HU'
    else:
        title = f'LMR{lmr_version} SST with HU'
    if rSST:
        title = title.replace('SST', 'rSST')
    if flor:
        title = title.replace(f'LMR{lmr_version}', 'FLOR').replace('sediment HU', 'HU')
    ax.set_title('') 
    ax.set_title(title, loc='center') 

if __name__ == '__main__':
    from wyconfig import * #my plot settings
    #from geoplots import mapplot
    from shared import axlabel
    plt.close()
    p_alpha = 0.1
    proj = ccrs.Robinson(central_longitude=180)
    dproj = ccrs.PlateCarree()
    fig, axes = plt.subplots(2, 2, figsize=(9,4.5), subplot_kw=dict(projection=proj))

    ax = axes[0, 0]
    wyplot(ds_lmr, slope=False, flor=False, ax=ax, p_alpha=p_alpha)

    ax = axes[0, 1]
    wyplot(ds_lmr, slope=True, flor=False, ax=ax, p_alpha=p_alpha)

    ax = axes[1, 0]
    wyplot(ds_flor, slope=False, flor=True, ax=ax, p_alpha=p_alpha)

    ax = axes[1, 1]
    wyplot(ds_flor, slope=True, flor=True, ax=ax, p_alpha=p_alpha)

    for ax,label in zip(axes.flat, list('ABCD')):
        axlabel(ax=ax, label=label)

    #savefig
    if len(sys.argv)>1 and 'savefig' in sys.argv or 's' in sys.argv:
        figname = __file__.replace('.py', f'.png')
        if rSST: figname = figname.replace('.png', '__rSST.png')
        if pyleoclim: figname= figname.replace('.png', '__pyleoclim.png')
        if p_alpha != 0.05: figname = figname.replace('.png', f'__alpha{int(p_alpha*100)}.png')
        if 'pdf' in sys.argv: figname = figname.replace('.png', '.pdf')
        if 'overwritefig' in sys.argv or 'o' in sys.argv:
            wysavefig(figname, overwritefig=True)
        else:
            wysavefig(figname)
    tt.check(f'**Done**')
    plt.show()
    
