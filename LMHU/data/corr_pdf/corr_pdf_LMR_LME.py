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
lme_case = 'fullForcing'
if 'volc' in sys.argv:
    lme_case = 'VOLC_GRA'
elif 'solar' in sys.argv:
    lme_case = 'SSI_VSK_L'
ofile = __file__.replace('.py', f'.lp{nwindow}.{years.start:04d}-{years.stop:04d}.nc')
if lme_case != 'fullForcing':
    ofile = ofile.replace('.nc', f'.{lme_case}.nc')
if os.path.exists(ofile):
    print('[loaded]:', ofile)
    reg = xr.open_dataset(ofile)
else:
    #da = xr.open_dataarray('../Lizzie/sedimentHU_v20220711ens_noCaySal.nc')
    da = xr.open_dataset('../LMR/LMR2019_ssttc_rMDRtransformed18702000.nc')['HU']
    da = xr.concat([da.mean('MCrun'), da], dim='MCrun') #first MCrun now is ens mean
    if lme_case == 'fullForcing':
        da1 = xr.open_dataset('../LME/LME_sstTC_fullForcing_13ens.nc')['HU']
        n_ens = 13
    elif lme_case == 'VOLC_GRA':
        da1 = xr.open_dataset('../LME/LME_sstTC_VOLC_GRA_5ens.nc')['HU']
        n_ens = 5
    elif lme_case == 'SSI_VSK_L':
        da1 = xr.open_dataset('../LME/LME_sstTC_SSI_VSK_L_4ens.nc')['HU']
        n_ens = 4
    da1 = xr.concat([da1.mean('ens'), da1.drop('ens')], dim='ens') #first ens now is ens mean
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
    n_ens = reg.ens.size - 1
    n_MCrun = reg.MCrun.size - 1
    #reg.r.plot.hist(bins=np.arange(-0.6,0.61,0.05), alpha=alpha, ax=ax, label='all')
    reg.r.sel(ens=slice(1,None), MCrun=slice(1,None)).plot.hist(bins=np.arange(-0.6,0.61,0.05), alpha=alpha, ax=ax, label=f'LMR {n_MCrun}ens and LME {lme_case} {n_ens}ens')
    reg.r.sel(ens=0).plot.hist(bins=np.arange(-0.6,0.61,0.05), alpha=alpha, ax=ax, label=f'LME {lme_case} ens mean')
    reg.r.sel(MCrun=0).plot.hist(bins=np.arange(-0.6,0.61,0.05), alpha=alpha, ax=ax, label=f'LMR ens mean')
    ax.set_ylabel('#')
    ax.legend(loc='upper left')
    #savefig
    if len(sys.argv)>1 and 'savefig' in sys.argv[1:]:
        figname = ofile.replace('.nc', f'.png')
        if 'overwritefig' in sys.argv[1:]:
            wysavefig(figname, overwritefig=True)
        else:
            wysavefig(figname)

    fig,ax = plt.subplots()
    #reg.r.plot.hist(bins=np.arange(-0.6,0.61,0.05), density=True, alpha=alpha, ax=ax, label='all')
    reg.r.sel(ens=slice(1,None), MCrun=slice(1,None)).plot.hist(bins=np.arange(-0.6,0.61,0.05), alpha=alpha, density=True, label=f'LMR {n_MCrun}ens and LME {lme_case} {n_ens}ens')
    reg.r.sel(ens=0).plot.hist(bins=np.arange(-0.6,0.61,0.05), alpha=alpha, density=True, label=f'LME {lme_case} ens mean')
    reg.r.sel(MCrun=0).plot.hist(bins=np.arange(-0.6,0.61,0.05), alpha=alpha, density=True, label=f'LMR ens mean')
    ax.set_ylabel('PDF')
    ax.legend(loc='upper left')
    
    #savefig
    if len(sys.argv)>1 and 'savefig' in sys.argv[1:]:
        figname = ofile.replace('.nc', f'.png')
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
    
