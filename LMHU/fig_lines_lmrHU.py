#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Fri Dec 31 10:07:19 EST 2021
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
#ds_sed = xr.open_dataset('data/Lizzie/sedimentHU_v20220103_noCaySal_smooth40yr_count.nc')
#ds_sed = xr.open_dataset('data/Lizzie/sedimentHU_v20220121_noCaySal_smooth40yr_count.nc')
#sediment HU
#ds_sed = xr.open_dataset('data/Lizzie/sedimentHU_v20220711ens_noCaySal_wy_max_lp40_count.nc') #wy 2022-08-08
ifile = 'data/Lizzie/sedimentHU_v20220711ens_noCaySal_wy_max_lp40_count.nc'
ifile_cached = __file__.replace('.py', '__sedimentHU.nc')
if not os.path.exists(ifile_cached) or 'od' in sys.argv: run_shell(f'cp {ifile} {ifile_cached}')
ds_sed = xr.open_dataset(ifile_cached)
print('[loaded]:', ifile_cached)
#LMR2018HU
#ds_lmr2018 = xr.open_dataset('data/LMR/LMR2018_ssttc_rMDRtransformed18702000_HU_lp40_CI95.nc')
ifile = 'data/LMR/LMR2018_ssttc_rMDRtransformed18702000_HU_lp40_CI95.nc'
ifile_cached = __file__.replace('.py', '__LMR2018HU.nc')
if not os.path.exists(ifile_cached) or 'od' in sys.argv: run_shell(f'cp {ifile} {ifile_cached}')
ds_lmr2018 = xr.open_dataset(ifile_cached)
print('[loaded]:', ifile_cached)
#LMR2019HU
#ds_lmr2019 = xr.open_dataset('data/LMR/LMR2019_ssttc_rMDRtransformed18702000_HU_lp40_CI95.nc')
ifile = 'data/LMR/LMR2019_ssttc_rMDRtransformed18702000_HU_lp40_CI95.nc'
ifile_cached = __file__.replace('.py', '__LMR2019HU.nc')
if not os.path.exists(ifile_cached) or 'od' in sys.argv: run_shell(f'cp {ifile} {ifile_cached}')
ds_lmr2019 = xr.open_dataset(ifile_cached)
print('[loaded]:', ifile_cached)
#modernHU
#ds_modern = xr.open_dataset('data/Vecchi2021/humh_adjusted_lowpass40.nc')
ifile = 'data/Vecchi2021/humh_adjusted_lowpass40.nc'
ifile_cached = __file__.replace('.py', '__modernHU.nc')
if not os.path.exists(ifile_cached) or 'od' in sys.argv: run_shell(f'cp {ifile} {ifile_cached}')
ds_modern = xr.open_dataset(ifile_cached)
print('[loaded]:', ifile_cached)

def wyplot(ax=None):
    if ax is None: fig, ax = plt.subplots(figsize=(8,3))
    alpha = 0.1
    lw = 2
    years = slice(850,2000)
    #sediment HU
    da = ds_sed['sedimentHUcount'].transpose().sel(year=years)#year,member -> member,year
    ax.fill_between(da.year, *da.sel(member=['lower_estimate', 'upper_estimate']).transpose('member', 'year'), color='gray', alpha=alpha)
    da.sel(member='sediment_estimate').plot(ax=ax, color='gray', label='sediment HU', lw=lw)
    #modern HU
    da = ds_modern['HU'].sel(year=years)
    ax.fill_between(da.year, *da.sel(quantile=[0.025, 0.975]), color='k', alpha=alpha)
    da.sel(quantile=0.5).plot(ax=ax, color='k', label='modern HU', lw=lw)
    #LMR2018-> LMR2.0
    da = ds_lmr2018['HU'].sel(year=years)
    ax.fill_between(da.year, *da.sel(quantile=[0.025, 0.975]), color='C0', alpha=alpha)
    da.sel(quantile=0.5).plot(ax=ax, color='C0', label='LMR2.0', lw=lw)
    #LMR2019-> LMR2.1
    da = ds_lmr2019['HU'].sel(year=years)
    ax.fill_between(da.year, *da.sel(quantile=[0.025, 0.975]), color='C1', alpha=alpha)
    da.sel(quantile=0.5).plot(ax=ax, color='C1', label='LMR2.1', lw=lw)

    ax.legend(ncol=4, loc='upper left')
    ax.set_xlim(years.start, years.stop)
    ax.set_xticks(range(2000,850,-100))
    ax.set_ylim(3,15)
    ax.set_yticks(range(3,16,2))
    ax.set_title('')
    ax.set_title('Hurricanes from statistical model using LMR SSTs', loc='left')
    ax.set_xlabel('year')
    ax.set_ylabel('HU count')
    
 
if __name__ == '__main__':
    from wyconfig import * #my plot settings
    plt.close()
    wyplot()
    
    #savefig
    if len(sys.argv)>1 and 'savefig' in sys.argv[1:]:
        figname = __file__.replace('.py', f'.png')
        if 'overwritefig' in sys.argv[1:]:
            wysavefig(figname, overwritefig=True)
        else:
            wysavefig(figname)
    tt.check(f'**Done**')
    plt.show()
    
