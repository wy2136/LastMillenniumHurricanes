#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Thu Jan 27 16:20:28 EST 2022
#readme: from FigS_heatmaps_corr_liz_lmr.py but HU only (exclude MH)
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
pyleoclim = True if 'pyleoclim' in sys.argv else False
#ifile = 'data/corr_table/corr_table_sedimentHUnoCaySal_vs_LMR2019HU_850-1850.nc'
ifile = 'data/corr_table/corr_table_sedimentMaxWyHUnoCaySal_vs_LMR2019HU_850-1850.nc' #wy 2022-08-08
if pyleoclim: ifile = ifile.replace('.nc', '_pyleoclim.nc')
#print(f'{ifile = }')
#ds_lmr2019_hu = xr.open_dataset(ifile)
ifile_cached = __file__.replace('.py', '__lmr2019hu.nc')
if pyleoclim: ifile_cached = ifile_cached.replace('.nc', '_pyleoclim.nc')
if not os.path.exists(ifile_cached): run_shell(f'cp {ifile} {ifile_cached}')
ds_lmr2019_hu = xr.open_dataset(ifile_cached)
print('[loaded]:', ifile_cached, 'from', ifile)

#ifile = 'data/corr_table/corr_table_sedimentHUnoCaySal_vs_LMR2019MH_850-1850.nc'
ifile = 'data/corr_table/corr_table_sedimentMaxWyHUnoCaySal_vs_LMR2019MH_850-1850.nc' #wy 2023-09-28
if pyleoclim: ifile = ifile.replace('.nc', '_pyleoclim.nc')
#print(f'{ifile = }')
#ds_lmr2019_mh = xr.open_dataset(ifile)
ifile_cached = __file__.replace('.py', '__lmr2019mh.nc')
if pyleoclim: ifile_cached = ifile_cached.replace('.nc', '_pyleoclim.nc')
if not os.path.exists(ifile_cached): run_shell(f'cp {ifile} {ifile_cached}')
ds_lmr2019_mh = xr.open_dataset(ifile_cached)
print('[loaded]:', ifile_cached, 'from', ifile)

#ifile = 'data/corr_table/corr_table_sedimentHUnoCaySal_vs_LMR2018HU_850-1850.nc'
ifile = 'data/corr_table/corr_table_sedimentMaxWyHUnoCaySal_vs_LMR2018HU_850-1850.nc' #wy 2022-08-08
if pyleoclim: ifile = ifile.replace('.nc', '_pyleoclim.nc')
#print(f'{ifile = }')
#ds_lmr2018_hu = xr.open_dataset(ifile)
ifile_cached = __file__.replace('.py', '__lmr2018hu.nc')
if pyleoclim: ifile_cached = ifile_cached.replace('.nc', '_pyleoclim.nc')
if not os.path.exists(ifile_cached): run_shell(f'cp {ifile} {ifile_cached}')
ds_lmr2018_hu = xr.open_dataset(ifile_cached)
print('[loaded]:', ifile_cached, 'from', ifile)

#ifile = 'data/corr_table/corr_table_sedimentHUnoCaySal_vs_LMR2018MH_850-1850.nc'
ifile = 'data/corr_table/corr_table_sedimentMaxWyHUnoCaySal_vs_LMR2018MH_850-1850.nc' #wy 2023-09-28
if pyleoclim: ifile = ifile.replace('.nc', '_pyleoclim.nc')
#print(f'{ifile = }')
#ds_lmr2018_mh = xr.open_dataset(ifile)
ifile_cached = __file__.replace('.py', '__lmr2018mh.nc')
if pyleoclim: ifile_cached = ifile_cached.replace('.nc', '_pyleoclim.nc')
if not os.path.exists(ifile_cached): run_shell(f'cp {ifile} {ifile_cached}')
ds_lmr2018_mh = xr.open_dataset(ifile_cached)
print('[loaded]:', ifile_cached, 'from', ifile)

#re-arrange jk-members to be consistent with the order of labels in the time series plot
jk_members = ['noNewEng', 'noMidAtl', 'noSoutheast', 'noGulfAppBay', 'noGulfChoBay',
    'noAbaco', 'noAndrosAM4', 'noLIBHBahamas', 'noMidCaicos', 'noVieqPR',
    'noYucatan', 'noLighthouse', 'allSites']
jk_members_new = jk_members.copy()
jk_members_new[3] = 'noGulfApaBay'
jk_members_new[11] = 'noLRBHBelize'
#revert the order of list
jk_members = jk_members[-1::-1]
jk_members_new = jk_members_new[-1::-1]
ds_lmr2019_hu = ds_lmr2019_hu.sel(member=jk_members).assign_coords(member=jk_members_new)
ds_lmr2019_mh = ds_lmr2019_mh.sel(member=jk_members).assign_coords(member=jk_members_new)
ds_lmr2018_hu = ds_lmr2018_hu.sel(member=jk_members).assign_coords(member=jk_members_new)
ds_lmr2018_mh = ds_lmr2018_mh.sel(member=jk_members).assign_coords(member=jk_members_new)

def wyplot(ds, ax=None):
    if ax is None:
        figsize = (8,4)
        fig, ax = plt.subplots(figsize=figsize)
    one_tailed = True
    alpha = 0.1
    da = ds.r
    p = ds.pvalue
    da.drop(['member', 'MCrun']).plot(ax=ax, vmax=1, cmap='RdBu_r')

    #add corr info to the plot; significant values are black
    for ii in range(da.member.size):
        for jj in range(da.MCrun.size):
            rr = da.isel(member=ii, MCrun=jj).item()
            pp = p.isel(member=ii, MCrun=jj).item()
            color = 'k' if pp<alpha else 'gray'
            if one_tailed:
                color = 'k' if pp<alpha*2 and rr>0 else 'gray'
            ax.text(jj, ii, f'{rr*100:2.0f}', ha='center', va='center', color=color)
    ax.set_yticks(range(da.member.size))
    ax.set_yticklabels(da.member.values)
    ax.set_xticks(range(da.MCrun.size))
    ax.set_xticklabels(da.MCrun.values)
    ax.set_xlabel('')
    ax.set_ylabel('')
 
if __name__ == '__main__':
    from wyconfig import * #my plot settings
    #figsize= 16/2,6.6
    #fig,axes = plt.subplots(2, 1, figsize=figsize, sharex=True, sharey=True, dpi=100)
    figsize= 16,6.6
    fig,axes = plt.subplots(2, 2, figsize=figsize, sharex=True, sharey=True, dpi=100)
    ax = axes[0,0]
    #ax = axes[0]
    wyplot(ds_lmr2019_hu, ax=ax)

    ax = axes[0,1]
    wyplot(ds_lmr2019_mh, ax=ax)

    ax = axes[1,0]
    #ax = axes[1]
    wyplot(ds_lmr2018_hu, ax=ax)

    ax = axes[1,1]
    wyplot(ds_lmr2018_mh, ax=ax)

    #for ax,title in zip(axes.flat, ['LMR2.1 HU', 'LMR2.1 MH', 'LMR2.0 HU', 'LMR2.0 MH']):
    for ax,title in zip(axes.flat, ['LMR2.1 HU', 'LMR2.1 MH',  'LMR2.0 HU', 'LMR2.0 MH']):
        ax.set_title(title)
    #for ax in axes[0,:]:
    #    ax.set_xlabel('')
    fig.suptitle('Heatmaps of correlations between sedimentary and LMR HU/MHs')
    
    #savefig
    if len(sys.argv)>1 and 'savefig' in sys.argv[1:] or 's' in sys.argv:
        figname = __file__.replace('.py', f'.png')
        if pyleoclim: figname = figname.replace('.png', f'__pyleoclim.png')
        if 'overwritefig' in sys.argv or 'o' in sys.argv:
            wysavefig(figname, overwritefig=True)
        else:
            wysavefig(figname)
    tt.check(f'**Done**')
    print()
    plt.show()
    
