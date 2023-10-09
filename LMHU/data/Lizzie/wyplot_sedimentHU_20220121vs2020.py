#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Thu Dec 23 16:01:21 EST 2021
if __name__ == '__main__':
    import sys
    from misc.timer import Timer
    s = ' '
    tt = Timer(f'start {s.join(sys.argv)}')
import sys, os.path, os, glob, datetime
import xarray as xr, numpy as np, pandas as pd, matplotlib.pyplot as plt
#more imports
#
if __name__ == '__main__':
    tt.check('end import')
#
#start from here
da2020 = xr.open_dataarray('sedimentHU_v20201219_smooth40yr.nc')
da_noCaySal = xr.open_dataarray('sedimentHU_v20220121_noCaySal_smooth40yr.nc')
da_wCaySal = xr.open_dataarray('sedimentHU_v20220121_wCaySal_smooth40yr.nc')
da_noCaySal_noCaicos = xr.open_dataarray('sedimentHU_v20220121_noCaySal_noCaicos_smooth40yr.nc')
years = slice(850, 2000)
yearsPI = slice(850, 1850)
sel_years = lambda da: da.sel(year=years)
sel_yearsPI = lambda da: da.sel(year=yearsPI)

def do_corrcoef(yearspan):
    da0 = da2020.sel(member='normTCcounts').sel(year=yearspan)
    da1 = da_noCaySal.sel(member='sediment_estimate').sel(year=yearspan)
    da2 = da_wCaySal.sel(member='sediment_estimate').sel(year=yearspan)
    da3 = da_noCaySal_noCaicos.sel(member='sediment_estimate').sel(year=yearspan)
    rg1 = da1.linregress.on(da0)
    rg2 = da2.linregress.on(da0)
    rg3 = da3.linregress.on(da0)
    return rg1.r.item(), rg2.r.item(), rg3.r.item()

if __name__ == '__main__':
    from wyconfig import * #my plot settings
    import xlinregress
    
    plt.close()
    fig, ax = plt.subplots(figsize=(8,3))
    da = da2020.sel(member=['smoothlower', 'smoothupper']).pipe(sel_years)
    ax.fill_between(da.year, *da.transpose(), color='C0', alpha=0.2)
    da = da2020.sel(member='normTCcounts').pipe(sel_years)
    da.plot(ax=ax, label='v2020')

    da = da_noCaySal_noCaicos.sel(member=['lower_estimate', 'upper_estimate']).pipe(sel_years)
    ax.fill_between(da.year, *da.transpose(), color='C1', alpha=0.2)
    da = da_noCaySal_noCaicos.sel(member='sediment_estimate').pipe(sel_years)
    da.plot(ax=ax, label='noCaySal_noCaicos(10)', ls='--')

    da = da_noCaySal.sel(member=['lower_estimate', 'upper_estimate']).pipe(sel_years)
    ax.fill_between(da.year, *da.transpose(), color='C2', alpha=0.2)
    da = da_noCaySal.sel(member='sediment_estimate').pipe(sel_years)
    da.plot(ax=ax, label='noCaySal(11)')

    da = da_wCaySal.sel(member=['lower_estimate', 'upper_estimate']).pipe(sel_years)
    ax.fill_between(da.year, *da.transpose(), color='C3', alpha=0.2)
    da = da_wCaySal.sel(member='sediment_estimate').pipe(sel_years)
    da.plot(ax=ax, label='wCaySal(12)', ls='--')

    ax.legend(loc='upper left', ncol=4)
    #cc850_2000 = do_corrcoef(slice(850, 2000)) #correlation coefficient
    r1, r2, r3 = do_corrcoef(yearsPI) #correlation coefficient
    ax.set_title(f'corr coef with v2020: {r3:.2g}(noCaySal_noCaicos);{r1:.2g}(noCaySal);{r2:.2g}(wCaySal)')
    ax.set_xlim(years.start, years.stop)
    ax.set_xticks(range(years.stop, years.start, -100))
    
    #savefig
    if len(sys.argv)>1 and 'savefig' in sys.argv[1:]:
        figname = __file__.replace('.py', f'.png')
        wysavefig(figname)
    tt.check(f'**Done**')
    plt.show()
    
