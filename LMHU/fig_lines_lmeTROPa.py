#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Mon Jan 10 13:38:55 EST 2022
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
#import xfilter
#n_window = 40
#lowpass = lambda da: da.filter.lowpass(1/n_window, dim='year', padtype='even')
 
#start from here
daname = 'TROPa'
#historical exps
ifile = f'data/LME/LME_{daname}_7cases_smooth40yr_ensmean.nc'
#ds = xr.open_dataset(ifile)
#print('[loaded]:', ifile)
ifile_cached = __file__.replace('.py', '.nc')
if not os.path.exists(ifile_cached): run_shell(f'cp {ifile} {ifile_cached}')
ds = xr.open_dataset(ifile_cached)
print('[loaded]:', ifile_cached, 'from', ifile)
#ctl exp
case_ctl = '0850cntl'
ifile = f'data/LME/LME_sstTC_{case_ctl}_{daname}_smooth40yr_spread.nc'
#ds_ctl = xr.open_dataset(ifile)
#print('[loaded]:', ifile)
ifile_cached = __file__.replace('.py', '__ctl.nc')
if not os.path.exists(ifile_cached): run_shell(f'cp {ifile} {ifile_cached}')
ds_ctl = xr.open_dataset(ifile_cached)
print('[loaded]:', ifile_cached, 'from', ifile)

def wyplot(ax=None):
    if ax is None:
        figsize = (8,3)
        fig, ax = plt.subplots(figsize=figsize)
    #full forcing exp
    case = 'fullForcing'
    label = f'{case}({ds.ens_size.sel(case=case).item()})'
    ds[daname].sel(case=case).plot(ax=ax, color='k', label=label, lw=2)

    #partial forcing exps
    ax.set_prop_cycle(None)
    for case in ds.case.values[1:]:
        label = f'{case}({ds.ens_size.sel(case=case).item()})'
        ds[daname].sel(case=case).plot(ax=ax, label=label, alpha=0.5)

    #cntl spread
    da = ds_ctl[daname]
    color, linestyle = 'gray', '--'
    ax.axhline(da.sel(quantile=2), color=color, ls=linestyle, label=f'{case_ctl} mean and 95% CI') #quantile = 2 denotes mean here
    ax.axhline(da.sel(quantile=0.025), color=color, ls=linestyle)
    ax.axhline(da.sel(quantile=0.975), color=color, ls=linestyle)


    ax.legend(ncol=3)
    if daname == 'HU':
        ax.set_ylim(5,11)
    elif daname == 'rMDRa':
        ax.set_ylim(-0.01, 0.4)
    elif daname == 'TROPa':
        ax.set_ylim(-0.7, 0.7)
    ax.set_xlim(850,2000)
    ax.set_xticks(range(2000,850,-100))
    ax.set_title('')
    if daname in ('HU', 'MH'):
        ax.set_ylabel(f'LME {daname} count')
    elif daname == 'rMDRa':
        ax.set_ylabel(f'LME MDR$-$TROP SST anom [K]')
    elif daname in ('TROPa',):
        ax.set_ylabel(f'LME TROP SST anom [K]')
        
 
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
    
