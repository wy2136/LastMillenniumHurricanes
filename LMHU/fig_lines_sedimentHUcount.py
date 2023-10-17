#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Wed Dec 29 17:47:17 EST 2021
if __name__ == '__main__':
    import sys
    from misc.timer import Timer
    s = ' '
    tt = Timer(f'start {s.join(sys.argv)}')
import sys, os.path, os, glob, datetime
import xarray as xr, numpy as np, pandas as pd, matplotlib.pyplot as plt
#more imports
from misc.shell import run_shell
#
if __name__ == '__main__':
    tt.check('end import')
#
#start from here
#ifile = 'data/Lizzie/sedimentHU_v20220103_noCaySal_smooth40yr_count.nc'
#ifile = 'data/Lizzie/sedimentHU_v20220121_noCaySal_smooth40yr_count.nc'
ifile = 'data/Lizzie/sedimentHU_v20220711ens_noCaySal_wy_max_lp40_count.nc' #wy 2022-08-08
#ds = xr.open_dataset(ifile)
#copy the original data file to the current dir
ifile_cached = __file__.replace('.py', '.nc')
if not os.path.exists(ifile_cached): run_shell(f'cp {ifile} {ifile_cached}')
ds = xr.open_dataset(ifile_cached)
print('[loaded]:', ifile_cached)
jk_color_list = plt.get_cmap('tab20')(np.linspace(0,1,20))
jk_members = ['noNewEng', 'noMidAtl', 'noSoutheast', 'noGulfAppBay', 'noGulfChoBay',
    'noAbaco', 'noAndrosAM4', 'noLIBHBahamas', 'noMidCaicos', 'noVieqPR',
    'noYucatan', 'noLighthouse']

#modern MH records
ifile = 'data/Vecchi2021/humh_adjusted_lowpass40.nc'
#da_mh = xr.open_dataset(ifile)['MH'].sel(year=slice(1870, 2000))
ifile_cached = __file__.replace('.py', '__MH.nc')
if not os.path.exists(ifile_cached): run_shell(f'cp {ifile} {ifile_cached}')
da_mh = xr.open_dataset(ifile_cached)['MH'].sel(year=slice(1870, 2000))
da_mhlf = xr.open_dataset(ifile_cached)['MHlandfall'].sel(year=slice(1870, 2000)) #landfall major hurricanes
print('[loaded]:', ifile_cached)

def wyplot(ax=None, MHon=False, landfallMHon=True):
    """MHon: if shows Major Hurricanes"""
    if ax is None:
        fig, ax = plt.subplots(figsize=(8,3))
    alpha = 0.2
    years = slice(850,2000)
    da = ds.sedimentHUcount.sel(year=years)
    ax.fill_between(da.year, da.isel(member=1), da.isel(member=2), alpha=alpha, color='gray')#, label='lower/upper')
    ax.set_prop_cycle(None)
    #for m in da.member.values[3:]:
    #    da.sel(member=m).plot(label=m, ax=ax, lw=1)
    for ii,m in enumerate(jk_members):
        label = m
        #if m == 'noLighthouse': label = 'noBelizeLRBH'
        if m == 'noLighthouse': label = 'noLRBHBelize'
        if m == 'noGulfAppBay': label = 'noGulfApaBay'
        da.sel(member=m).plot(label=label, ax=ax, lw=1, ls='-', color=jk_color_list[ii])
        
    #da.isel(member=slice(4,None)).plot(hue='member', lw=1, ax=ax)
    da.isel(member=0).plot(lw=2, color='gray', ls='-', ax=ax, label='all sites')

    #modern HU records
    da_gv = ds.HUrecord.sel(year=slice(1870,2000))
    ax.fill_between(da_gv.year, *da_gv.sel(quantile=[0.025, 0.975]), alpha=alpha, color='k')
    da_gv.sel(quantile=0.5).plot(lw=2, color='k', ls='-', ax=ax, label='modern HU record')

    ax.legend(ncol=4, loc='upper left')
    ax.set_ylabel('HU count')
    ax.set_ylim(3,15)
    ax.set_yticks(range(3,16,2))
    ax.set_xlim(years.start, years.stop)
    ax.set_xticks(range(2000,850,-100))
    ax.set_title('')
    ax.set_title('Hurricanes from sediment reconstructions and modern record', loc='left')

    #modern MH records
    if MHon:
        ax_twin = ax.twinx()
        ax_twin.fill_between(da_mh.year, *da_mh.sel(quantile=[0.025, 0.975]), alpha=alpha, color='k')
        da_mh.sel(quantile=0.5).plot(lw=2, color='k', ls='--', ax=ax_twin, label='modern MH record')
        if landfallMHon:
            #shift/scale landfall MH to have the same mean and std as the MH
            mhMean = da_mh.sel(quantile=0.5).mean()
            mhSTD = da_mh.sel(quantile=0.5).std()
            mhlfMean = da_mhlf.mean()
            mhlfSTD = da_mhlf.std()
            da_ = (da_mhlf - mhlfMean)/mhlfSTD * mhSTD + mhMean
            da_.plot(lw=2, color='k', ls=':', ax=ax_twin, label='modern landfall MH record (scaled)')
        #reset the ylim of ax_twin
        huMean = da_gv.sel(quantile=0.5).mean()
        huSTD = da_gv.sel(quantile=0.5).std()
        mhMean = da_mh.sel(quantile=0.5).mean()
        mhSTD = da_mh.sel(quantile=0.5).std()
        ymin, ymax = ax.get_ylim()
        ymin_twin = (ymin - huMean)/huSTD * mhSTD + mhMean
        ymax_twin = (ymax - huMean)/huSTD * mhSTD + mhMean
        ax_twin.set_ylim(ymin_twin, ymax_twin)
        #other settings for ax_twin
        ax_twin.spines['right'].set_visible(True)
        ax_twin.spines['left'].set_visible(False)
        ax_twin.set_title('')
        ax_twin.set_ylabel('MH count')
        ax_twin.grid(False)
        ax.get_legend().remove()
        ax_twin.legend()

        ax_twin.set_xlim(1870,2000)
        
        
 
 
if __name__ == '__main__':
    from wyconfig import * #my plot settings
    plt.close()
    wyplot(MHon=False)
    #fig,ax = plt.subplots()
    #wyplot(MHon=True, ax=ax)
    
    #savefig
    if len(sys.argv)>1 and 'savefig' in sys.argv[1:] or 's' in sys.argv:
        figname = __file__.replace('.py', f'.png')
        if 'overwritefig' in sys.argv[1:] or 'o' in sys.argv:
            wysavefig(figname, overwritefig=True)
        else:
            wysavefig(figname)

    fig,ax = plt.subplots()
    wyplot(MHon=True, landfallMHon=True, ax=ax)

    #savefig
    if len(sys.argv)>1 and 'savefig' in sys.argv[1:] or 's' in sys.argv:
        figname = __file__.replace('.py', f'__MHon.png')
        if 'overwritefig' in sys.argv[1:] or 'o' in sys.argv:
            wysavefig(figname, overwritefig=True)
        else:
            wysavefig(figname)

    tt.check(f'**Done**')
    plt.show()
    
