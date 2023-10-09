#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Wed Jan  4 10:21:22 EST 2023
if __name__ == '__main__':
    import sys
    from misc.timer import Timer
    tt = Timer('start ' + ' '.join(sys.argv))
import sys, os.path, os, glob, datetime
import xarray as xr, numpy as np, pandas as pd, matplotlib.pyplot as plt
#more imports
#
if __name__ == '__main__':
    tt.check('end import')
#
#start from here
lmr = '2018' if '2018' in sys.argv else '2019'
ifile = f'/tigress/gvecchi/DATA/LMR_{lmr}/sst_MCruns_ensemble_mean.nc'
years = slice('0850', '1850')
years_ref = slice('1901', '2000')
long_name=f'LMR{lmr} SSTa over {years.start}-{years.stop} with ref to {years_ref.start}-{years_ref.stop}'

#ofile after anomaly and ens/time mean
ofile = f'LMR{lmr}_ssta_{years.start}-{years.stop}_ref{years_ref.start}-{years_ref.stop}.nc'
if os.path.exists(ofile):
    print('[exists]:', ofile)
    daa = xr.open_dataarray(ofile)
else:
    da = xr.open_dataarray(ifile).load()
    daa = da.sel(time=years).mean('time').mean('MCrun') - da.sel(time=years_ref).mean('time').mean('MCrun')
    daa = daa.assign_attrs(units='K', long_name=long_name)
    daa.to_dataset(name='sst').to_netcdf(ofile)
    print('[saved]:', ofile)

if __name__ == '__main__':
    from wyconfig import * #my plot settings
    daa.plot.contourf(levels=21)
    ax = plt.gca()
    ax.set_title(long_name)
    
    #savefig
    if 'savefig' in sys.argv or 's' in sys.argv:
        tag = long_name.replace(' ', '_')
        figname = __file__.replace('.py', f'_{tag}.png')
        if 'overwritefig' in sys.argv or 'o' in sys.argv:
            wysavefig(figname, overwritefig=True)
        else:
            wysavefig(figname)
    tt.check(f'**Done**')
    print()
    if 'notshowfig' in sys.argv:
        pass
    else:
        plt.show()
    
