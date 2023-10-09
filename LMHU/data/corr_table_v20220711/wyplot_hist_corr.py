#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Thu Jan 27 13:26:49 EST 2022
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
ifile = 'corr_table_sedimentHUnoCaySal_vs_LMR2019HU_850-1850.nc'
case = 'noCaySal'
lmr = 2019
daname = 'r'
one_tailed = True
if len(sys.argv)>1:
    if 'wCaySal' in sys.argv[1:]:
        case = 'wCaySal'
    elif 'noCaySal_noCaicos' in sys.argv[1:]:
        case = 'noCaySal_noCaicos'

    if '2018' in sys.argv[1:]:
        lmr = 2018

    if 'pvalue' in sys.argv[1:]:
        daname = 'pvalue'
print(f'{case = }; {lmr = }; {daname = }')
ifile = ifile.replace('noCaySal', case).replace('LMR2019', f'LMR{lmr}')
print(f'{ifile = }')
ds = xr.open_dataset(ifile)
 
 
if __name__ == '__main__':
    from wyconfig import * #my plot settings
    fig, ax = plt.subplots()
    if daname == 'r':
        bins = np.arange(-0.3, 0.51, 0.05)
    elif daname == 'pvalue':
        bins = np.arange(0, 0.51, 0.05)
    da = ds[daname]
    if daname == 'pvalue' and one_tailed:
        da = da/2
    da.plot.hist(bins=bins, ax=ax, label='all')
    da.isel(MCrun=0).plot.hist(bins=bins, label='LMR-ens-mean only')

    ax.legend()
    ax.set_ylabel('#')
    title = f'sediment HU ({case}) and LMR{lmr} HU: {daname}'
    if daname == 'pvalue' and one_tailed:
        title += '(one tailed)'
    ax.set_title(title)

    #savefig
    if len(sys.argv)>1 and 'savefig' in sys.argv[1:]:
        #figname = __file__.replace('.py', f'.png')
        figname = __file__.replace('.py', f'_{case}_LMR{lmr}_{daname}.png')
        if 'overwritefig' in sys.argv[1:]:
            wysavefig(figname, overwritefig=True)
        else:
            wysavefig(figname)
    tt.check(f'**Done**')
    print()
    plt.show()
    
