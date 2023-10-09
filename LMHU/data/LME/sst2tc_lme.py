#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Fri Jan  7 11:41:31 EST 2022
if __name__ == '__main__':
    import sys
    from misc.timer import Timer
    tt = Timer('start ' + ' '.join(sys.argv))
import sys, os.path, os, glob, datetime
import xarray as xr, numpy as np, pandas as pd, matplotlib.pyplot as plt
#more imports
from sst2tc_lme_core import sst2tc
#
if __name__ == '__main__':
    tt.check('end import')
#
#start from here
#do the fullForcing experiment first
expname = sys.argv[1] if len(sys.argv)>1 else 'fullForcing'

idir = '/tigress/gvecchi/DATA/CESM/LME/SST'
if expname == 'fullForcing':
    ifiles = f'{idir}/b.e11.BLMTRC5CN.f19_g16.???.*.nc'
    n_ens = 13
    ens = range(1, n_ens+1)
elif expname == 'GHG':
    ifiles = f'{idir}/b.e11.BLMTRC5CN.f19_g16.{expname}.???.*.nc'
    n_ens = 3
    ens = range(1, n_ens+1)
elif expname == 'VOLC_GRA':
    ifiles = f'{idir}/b.e11.BLMTRC5CN.f19_g16.{expname}.???.*.nc'
    n_ens = 5
    ens = range(1, n_ens+1)
elif expname == 'LULC_HurttPongratz':
    ifiles = f'{idir}/b.e11.BLMTRC5CN.f19_g16.{expname}.???.*.nc'
    n_ens = 3 
    ens = range(1, n_ens+1)
elif expname == 'SSI_VSK_L':
    ifiles = f'{idir}/b.e11.BLMTRC5CN.f19_g16.{expname}.???.*.nc'
    ens = [1,] + list(range(3, 5+1))
    n_ens = len(ens) 
elif expname == 'ORBITAL':
    ifiles = f'{idir}/b.e11.BLMTRC5CN.f19_g16.{expname}.???.*.nc'
    n_ens = 3 
    ens = range(1, n_ens+1)
elif expname == 'OZONE_AER':
    ifiles = f'{idir}/b.e11.BLMTRC5CN.f19_g16.{expname}.???.*.nc'
    n_ens = 3 
    ens = range(1, n_ens+1)
elif expname == '0850cntl':
    ifiles = f'{idir}/b.e11.B1850C5CN.f19_g16.{expname}.001.*.nc'
    ens = None
elif expname == '850forcing':
    ifiles = f'{idir}/b.e11.BLMTRC5CN.f19_g16.{expname}.003.*.nc'
    ens = None
else:
    print('The input expname is wrong!')
    sys.exit()
    
yearsRef = slice(1982, 2005) # reference years in calculation of sst anomaly for TC indices
fullForcingRef = False if expname=='fullForcing' else True # use the ensemble mean of MDR/TROP sst from the fullForcing simulation as the reference; run the case of False first to get the necessary data
if expname in ('0850cntl', '850forcing'): # control runs, no ensembles
    ofile = f'LME_sstTC_{expname}.nc'
else:
    ofile = f'LME_sstTC_{expname}_{n_ens}ens.nc'
#if fullForcingRef:
#    ofile = ofile.replace('.nc', '.fullForcingRef.nc')
if os.path.exists(ofile):
    print('[exists]:', ofile)
    sys.exit()
     
if expname in ('0850cntl', '850forcing'): # control runs, no ensembles
    print(expname, ifiles)
    sst2tc(ifiles, ofile, yearsRef=yearsRef, fullForcingRef=fullForcingRef)
else: #exps with ensembles
    print(expname, n_ens, 'ens', ifiles)
    dss = []
    for en in ens:
        print(f'en = {en:02d}/{n_ens:02d}')
        _ifiles = ifiles.replace('???', f'{en:03d}')
        ds = sst2tc(_ifiles, yearsRef=yearsRef, fullForcingRef=fullForcingRef)
        ds.load()
        dss.append(ds)

    # concat
    print('concatenating...')
    ds_o = xr.concat(dss, dim=pd.Index(ens, name='ens'))
    #print('loading ...')
    #ds_o.load()

    # save to nc
    print('saving to', ofile, '...')
    encoding = {v:{'_FillValue': None, 'dtype': 'float32'}
        for v in ['HU', 'TS', 'PDI', 'MDR', 'TROP']}
    encoding['year'] = {'_FillValue': None, 'dtype': 'int32'}
    encoding['ens'] = {'_FillValue': None, 'dtype': 'int32'}
    ds_o.to_netcdf(ofile, encoding=encoding)
    print('[saved]:', ofile)
    
if __name__ == '__main__':
    #from wyconfig import * #my plot settings
    
    #savefig
    if len(sys.argv)>1 and 'savefig' in sys.argv[1:]:
        figname = __file__.replace('.py', f'.png')
        if 'overwritefig' in sys.argv[1:]:
            wysavefig(figname, overwritefig=True)
        else:
            wysavefig(figname)
    tt.check(f'**Done**')
    #plt.show()
