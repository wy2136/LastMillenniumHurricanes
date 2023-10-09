#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Thu Jul 21 15:39:07 EDT 2022
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
ifile = 'sedimentHU_v20220711ens_noCaySal_wy_max_lp40.nc'
da = xr.open_dataarray(ifile)

ifile = 'sedimentHU_v20220711ens_noCaySal_wy_max_lp40_ageerr.nc'
da1 = xr.open_dataarray(ifile)
 
 
if __name__ == '__main__':
    from wyconfig import * #my plot settings
    fig,ax = plt.subplots()
    alpha = 0.3
    ax.fill_between(da.year, *da1.isel(member=slice(1,3)), alpha=alpha, color='C0', label='age + jackknife')
    ax.fill_between(da.year, *da.isel(member=slice(1,3)), alpha=alpha, color='C1', label='jackknife')
    da.isel(member=0).plot(color='k')
    ax.legend()
    
    #savefig
    if len(sys.argv)>1 and 'savefig' in sys.argv[1:]:
        figname = __file__.replace('.py', f'.png')
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
    
