#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Thu Jan 13 10:17:37 EST 2022
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
#da_w = xr.open_dataarray('sedimentHU_v20220112_wCaySal_smooth40yr.nc')
#da_no = xr.open_dataarray('sedimentHU_v20220112_noCaySal_smooth40yr.nc')
da_w = xr.open_dataarray('sedimentHU_v20220121_wCaySal_smooth40yr.nc')
da_no = xr.open_dataarray('sedimentHU_v20220121_noCaySal_smooth40yr.nc')

if __name__ == '__main__':
    from wyconfig import * #my plot settings
    fig, ax = plt.subplots(figsize=(8,3))
    da_w.sel(member='noCaySal').plot(label='wCaySal version (12 region), noCaySal jk member', ax=ax)
    da_no.sel(member='sediment_estimate').plot(label='noCaySal version (11 region), sediment estimate', ls='--', ax=ax)

    ax.legend()
    ax.set_title('')
    
    #savefig
    if len(sys.argv)>1 and 'savefig' in sys.argv[1:]:
        figname = __file__.replace('.py', f'.png')
        if 'overwritefig' in sys.argv[1:]:
            wysavefig(figname, overwritefig=True)
        else:
            wysavefig(figname)
    tt.check(f'**Done**')
    plt.show()
    
