#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Tue Jul 19 13:29:07 EDT 2022
if __name__ == '__main__':
    import sys
    from misc.timer import Timer
    tt = Timer('start ' + ' '.join(sys.argv))
import sys, os.path, os, glob, datetime
import xarray as xr, numpy as np, pandas as pd, matplotlib.pyplot as plt
#more imports
import xfilter
import xlinregress
#
if __name__ == '__main__':
    tt.check('end import')
#
#start from here
nwindow = 40
lowpass = lambda x: x.filter.lowpass(1/nwindow, dim='year', padtype='even')
years = slice(850,1850)
lme_case = '0850cntl'
ofile = __file__.replace('.py', f'.lp{nwindow}.{years.start:04d}-{years.stop:04d}.nc')
if os.path.exists(ofile):
    print('[loaded]:', ofile)
    reg = xr.open_dataset(ofile)
else:
    da = xr.open_dataarray('../Lizzie/sedimentHU_v20220711ens_noCaySal.nc')
    #da1 = xr.open_dataset('../LMR/LMR2019_ssttc_rMDRtransformed18702000.nc')['HU']
    #if lme_case == 'fullForcing':
    #    da1 = xr.open_dataset('../LME/LME_sstTC_fullForcing_13ens.nc')['HU']
    #    n_ens = 13
    da1 = xr.open_dataset('../LME/LME_sstTC_0850cntl.nc')['HU']
    da_lp = da.pipe(lowpass).sel(year=years)
    da1_lp = da1.pipe(lowpass).sel(year=years)
    reg = da_lp.linregress.on(da1_lp, dim='year')
    #save
    reg.to_netcdf(ofile)
    print('[saved]:', ofile)

if __name__ == '__main__':
    from wyconfig import * #my plot settings
    alpha = 0.5
    fig,ax = plt.subplots()
    #reg.r.plot.hist(bins=np.arange(-0.6,0.61,0.01), alpha=alpha, ax=ax, label='all')
    reg.r.plot.hist(bins=np.arange(-0.6,0.61,0.01), alpha=alpha, ax=ax, label=f'LME {lme_case}')
    ax.set_ylabel('#')
    ax.legend()
    #savefig
    if len(sys.argv)>1 and 'savefig' in sys.argv[1:]:
        figname = __file__.replace('.py', f'.png')
        if 'overwritefig' in sys.argv[1:]:
            wysavefig(figname, overwritefig=True)
        else:
            wysavefig(figname)

    fig,ax = plt.subplots()
    #reg.r.plot.hist(bins=np.arange(-0.6,0.61,0.01), density=True, alpha=alpha, ax=ax, label='all')
    reg.r.plot.hist(bins=np.arange(-0.6,0.61,0.01), alpha=alpha, density=True, label=f'LME {lme_case}')
    ax.set_ylabel('PDF')
    ax.legend()
    
    #savefig
    if len(sys.argv)>1 and 'savefig' in sys.argv[1:]:
        figname = __file__.replace('.py', f'.png')
        figname = figname.replace('.png', '_density.png')
        if 'overwritefig' in sys.argv[1:]:
            wysavefig(figname, overwritefig=True)
        else:
            wysavefig(figname)
    tt.check(f'**Done**')
    print()
    if 'notshowfig' in sys.argv:
        pass
    else:
        plt.show()
    
