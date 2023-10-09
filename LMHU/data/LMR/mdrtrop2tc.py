#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Wed May 26 21:05:02 EDT 2021
if __name__ == '__main__':
    from misc.timer import Timer
    tt = Timer(f'start {__file__}')
import sys, os.path, os, glob, datetime
import xarray as xr, numpy as np, pandas as pd, matplotlib.pyplot as plt
#more imports
#
if __name__ == '__main__':
    tt.check('end import')
#
#start from here
yearsRef = None#slice(1982,2005)
if len(sys.argv)>1:
    ifile = sys.argv[1]
else:
    print('please provide the input data file that includes MDR/TROP SSTs')
    sys.exit()
print('[ifile]:', ifile)
ofile = ifile.replace('sstmdrtrop', 'ssttc')
print('[ofile]', ofile)
if os.path.exists(ofile):
    print('[exists]:', ofile)
    sys.exit()
ds = xr.open_dataset(ifile)
if True:
    #MDRa, TROPa
    MDR,TROP = ds.MDR,ds.TROP
    #MDRa = MDR - MDR.sel(year=yearsRef).mean('year')
    #TROPa = TROP - TROP.sel(year=yearsRef).mean('year')
    #MDR/TROP from LMR2018_sstmdrtrop.nc/LMR2019_sstmdrtrop.nc are already anomalies
    MDRa = MDR
    TROPa = TROP
    #co2 for MH
    years = MDR.year.values
    co2 = xr.open_dataarray('/tigress/wenchang/data/cmip6/input/ghg/co2glbmean_0000-2500_ssp585.nc')
    co2 = co2.sel(year=slice(years[0], years[-1]))#only keep years overlaped with MDR/TROP
    logco2a = np.log(co2/co2.sel(year=1990))

    #HU (hurricane #)
    HU = np.exp(1.707 + 1.388*MDRa - 1.521*TROPa)
    HU.attrs['long_name'] = 'HU#: EXP(1.707 + 1.388*MDRa - 1.521*TROPa)'
    if yearsRef:
        HU.attrs['yearsRef'] = f'{yearsRef.start}-{yearsRef.stop}'

    #MH (major hurricane #)
    MH = np.exp(-0.01678 + 2.19472*MDRa - 1.79117*TROPa - 0.38783*logco2a)
    MH.attrs['long_name'] = 'MH#: EXP(-0.01678 + 2.19472*MDRa - 1.79117*TROPa - 0.38783*logco2a)'
    if yearsRef:
        MH.attrs['yearsRef'] = f'{yearsRef.start}-{yearsRef.stop}'

    #MH (major hurricane #) without using CO2
    MHnoCO2 = np.exp(-0.01678 + 2.19472*MDRa - 1.79117*TROPa)# - 0.38783*logco2a)
    MHnoCO2.attrs['long_name'] = 'MH#: EXP(-0.01678 + 2.19472*MDRa - 1.79117*TROPa)'# - 0.38783*logco2a)'
    if yearsRef:
        MHnoCO2.attrs['yearsRef'] = f'{yearsRef.start}-{yearsRef.stop}'

    #TS (tropical storm #)
    TS = np.exp(2.10356 + 0.97612*MDRa - 0.97102*TROPa)
    TS.attrs['long_name'] = 'TS#: EXP(2.10356 + 0.97612*MDRa - 0.97102*TROPa)'
    if yearsRef:
        TS.attrs['yearsRef'] = f'{yearsRef.start}-{yearsRef.stop}'

    #PDI
    PDI = np.exp(0.76 + 1.87*MDRa - 1.58*TROPa)
    PDI.attrs['long_name'] = 'PDI: EXP(0.76 + 1.87*MDRa - 1.58*TROPa)'
    if yearsRef:
        PDI.attrs['yearsRef'] = f'{yearsRef.start}-{yearsRef.stop}'
 
    ds['HU'] = HU
    ds['MH'] = MH
    ds['MHnoCO2'] = MHnoCO2
    ds['TS'] = TS
    ds['PDI'] = PDI
    ds['co2'] = co2

print('saving...') 
ds.to_netcdf(ofile)
print('[saved]:', ofile)

if __name__ == '__main__':
    #from wyconfig import * #my plot settings
    
    #savefig
    if 'savefig' in sys.argv:
        figname = __file__.replace('.py', f'.png')
        wysavefig(figname)
    tt.check(f'**Done**')
    plt.show()
    
