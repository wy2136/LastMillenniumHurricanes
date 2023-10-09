#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Mon Aug  8 17:40:39 EDT 2022
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
#ifile = 'data/corr_pdf/corr_pdf_sedimentHU_LMR2019HU_lp40_0850-1850.nc'
#ds2019 = xr.open_dataset(ifile)
#ifile = 'data/corr_pdf/corr_pdf_sedimentHU_LMR2018HU_lp40_0850-1850.nc'
#ds2018 = xr.open_dataset(ifile)
ifile = 'data/corr_pdf/corr_pdf_sedimentHU_LME.lp40.0850-1850.nc'
#ds = xr.open_dataset(ifile)
ifile_cached = __file__.replace('.py', '.nc')
if not os.path.exists(ifile_cached): run_shell(f'cp {ifile} {ifile_cached}')
ds = xr.open_dataset(ifile_cached)
print('[loaded]:', ifile_cached, '**from**', ifile)
 
 
if __name__ == '__main__':
    from wyconfig import * #my plot settings
    fig, ax = plt.subplots()
    alpha = 0.5
    bins = np.arange(-0.6,0.61,0.01)
    ds['r'].plot.hist(bins=bins, density=True, alpha=alpha, ax=ax)

    ax.set_ylabel('PDF')
    #ax.legend(loc='upper left')
    ax.set_title('Correlation between sediment HUs and LME SST emulated HUs')
    
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
    
