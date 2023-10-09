#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Tue Jul 19 11:10:46 EDT 2022
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
ifile = 'raw/2022-07-11/Reg12_nosmooth_2022.nc'
ofile = __file__.replace('.py', '_noCaySal.nc')
if 'wCaySal' in sys.argv:
    ifile = ifile.replace('Reg12', 'Reg13')
    ofile = ofile.replace('noCaySal', 'wCaySal')
if os.path.exists(ofile):
    print('[exists]:', ofile)
    #sys.exit()
ds  = xr.open_dataset(ifile)
ds = ds.rename(iter='mc', nreg='jk', time='year')
jkmembers = [name.replace('No_', 'no').replace('_', '') for name in ds.jk.attrs['Names']]
sedimentHU = xr.concat([ds.TC_all.expand_dims('jk').assign_coords(jk=['allSites']), ds.TC_jk.assign_coords(jk=jkmembers)], dim='jk')
sedimentHU = sedimentHU.sortby(sedimentHU.jk)
#mc, year: float->int
mc_new = sedimentHU.mc.values.astype('int')
year_new = sedimentHU.year.values.astype('int')
sedimentHU = sedimentHU.assign_coords(mc=mc_new, year=year_new)

#save
sedimentHU.to_dataset(name='sedimentHU').to_netcdf(ofile, encoding=dict(sedimentHU=dict(zlib=True, complevel=1)))
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
    print()
    if 'notshowfig' in sys.argv:
        pass
    else:
        plt.show()
