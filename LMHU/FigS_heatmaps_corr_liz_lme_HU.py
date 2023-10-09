#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Thu Jan 27 15:24:57 EST 2022
#readme: from FigS_heatmaps_corr_liz_lme.py but HU only (exclude MH)
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
#ifile = 'data/corr_table/corr_table_sedimentHUnoCaySal_vs_lmeHU_850-1850.nc'
ifile = 'data/corr_table_v20220711/corr_table_sedimentMaxWyHUnoCaySal_vs_lmeHU_850-1850.nc'
#ds_hu = xr.open_dataset(ifile)
#print(f'{ifile = }')
ifile_cached = __file__.replace('.py', '.nc')
if not os.path.exists(ifile_cached): run_shell(f'cp {ifile} {ifile_cached}')
ds_hu = xr.open_dataset(ifile_cached)
print('[loaded]:', ifile_cached, '**from**', ifile)

#ifile = 'data/corr_table/corr_table_sedimentHUnoCaySal_vs_lmeMH_850-1850.nc'
#ds_mh = xr.open_dataset(ifile)
#print(f'{ifile = }')

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
ds_hu = ds_hu.sel(member=jk_members).assign_coords(member=jk_members_new)

def wyplot(ds, ax=None):
    if ax is None:
        figsize = (8,4)
        fig, ax = plt.subplots(figsize=figsize)
    one_tailed = True
    alpha = 0.1
    da = ds.r
    p = ds.pvalue

    da.drop(['member', 'ens']).plot(ax=ax, vmax=1, cmap='RdBu_r')

    #add corr info to the plot; significant values are black
    for ii in range(da.member.size):
        for jj in range(da.ens.size):
            rr = da.isel(member=ii, ens=jj).item()
            pp = p.isel(member=ii, ens=jj).item()
            color = 'k' if pp<alpha else 'gray'
            if one_tailed:
                color = 'k' if pp<alpha*2 and rr>0 else 'gray'
            ax.text(jj, ii, f'{rr*100:2.0f}', ha='center', va='center', color=color)
    ax.set_yticks(range(da.member.size))
    ax.set_yticklabels(da.member.values)
    ax.set_xticks(range(da.ens.size))
    ax.set_xticklabels(da.ens.values)
    ax.set_xlabel('')
    ax.set_ylabel('')
 
 
if __name__ == '__main__':
    from wyconfig import * #my plot settings
    """
    fig, axes = plt.subplots(2, 1, figsize=(8,7), sharex=True)
    ax = axes[0]
    wyplot(ds_hu, ax=ax)
    ax.set_title('LME HU')
    
    ax = axes[1]
    wyplot(ds_mh, ax=ax)
    ax.set_title('LME MH')
    ax.set_xlabel('LME ensemble member')
    """
    fig, ax = plt.subplots()
    wyplot(ds_hu, ax=ax)
    ax.set_xlabel('LME ensemble member')
    
    #savefig
    if len(sys.argv)>1 and 'savefig' in sys.argv[1:] or 's' in sys.argv:
        figname = __file__.replace('.py', f'.png')
        if 'overwritefig' in sys.argv[1:]:
            wysavefig(figname, overwritefig=True)
        else:
            wysavefig(figname)
    tt.check(f'**Done**')
    print()
    plt.show()
    
