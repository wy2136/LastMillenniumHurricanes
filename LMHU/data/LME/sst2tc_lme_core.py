#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Thu Jan  6 17:12:20 EST 2022
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
#ifiles = 'LME_SST/b.e11.B1850C5CN.f19_g16.0850cntl.001.*.nc'
#ofile = 'LME_TC.0850cntl.nc'
#sstName = 'SST'
#xName = 'nlon'
#yName = 'nlat'
#latName = 'TLAT'
#lonName = 'TLONG'
#areaName = 'TAREA'
#shiftTimeAxis = True #CESM data time axis is one month late and needs a backward shift
#yearsRef = slice(1982, 2005) # reference years in calculation of sst anomaly for TC indices

def sst2tc(ifiles, ofile=None, sstName='SST', xName='nlon', yName='nlat', lonName='TLONG', latName='TLAT', areaName='TAREA', shiftTimeAxis=True, yearsRef=None, fullForcingRef=False):
    # fullForcingRef: whether to use reference SSTs of MDR and TROP from the fullForcing experiment
    if fullForcingRef:
        fullForcingTCfile = 'LME_sstTC_fullForcing_13ens.nc'
        ds_fullForcingTC = xr.open_dataset(fullForcingTCfile)
    print('[ifiles]:', ifiles)
    ds = xr.open_mfdataset(ifiles)
    #ds.load()
    if shiftTimeAxis:
        ds['time'] = ds.indexes['time'].shift(-1, 'MS')
        print('[time shifted]:', 'one month back')
    sst = ds[sstName].squeeze()
    if 'z_t' in list(sst.coords):
        sst = sst.drop('z_t')
        print('[coords dropped]:', 'z_t')
    area = ds[areaName] + sst*0 # apply the sst mask to area
    lon = ds[lonName]
    lat = ds[latName]

    #MDR(main development region)
    inMDR = (lat>=10)&(lat<=25)&(lon>=280)&(lon<=340)
    sst_ = sst.where(inMDR)
    area_ = area.where(inMDR)
    MDR = (sst_*area_).sum([xName, yName])/area_.sum([xName, yName]) # area mean
    MDR = MDR.groupby('time.year').mean('time') # yearly mean
    MDR.attrs = sst.attrs
    MDR.attrs['long_name'] = 'MDR ' + MDR.attrs['long_name']
    if yearsRef is not None:
        if fullForcingRef:
            MDRa = MDR - ds_fullForcingTC.MDR.sel(year=yearsRef).mean('year').mean('ens')
        else:
            MDRa = MDR - MDR.sel(year=yearsRef).mean('year')
    else:
        MDRa = MDR - MDR.mean('year')
    MDRa.attrs['long_name'] = 'MDR SST anomaly'
    if yearsRef:
        MDRa.attrs['yearsRef'] = f'{yearsRef.start}-{yearsRef.stop}'
    if fullForcingRef:
        MDRa.attrs['expRef'] = f'fullForcing ensemble mean'

    #TROP (tropical reagion)
    inTROP = (lat>=-30)&(lat<=30)
    sst_ = sst.where(inTROP)
    area_ = area.where(inTROP)
    TROP = (sst_*area_).sum([xName, yName])/area_.sum([xName, yName]) # area mean
    TROP = TROP.groupby('time.year').mean('time') # yearly mean
    TROP.attrs = sst.attrs
    TROP.attrs['long_name'] = 'TROP ' + TROP.attrs['long_name']
    if yearsRef is not None:
        if fullForcingRef:
            TROPa = TROP - ds_fullForcingTC.TROP.sel(year=yearsRef).mean('year').mean('ens')
        else:
            TROPa = TROP - TROP.sel(year=yearsRef).mean('year')
    else:
        TROPa = TROP - TROP.mean('year')
    TROPa.attrs['long_name'] = 'TROP SST anomaly'
    if yearsRef:
        TROPa.attrs['yearsRef'] = f'{yearsRef.start}-{yearsRef.stop}'
    if fullForcingRef:
        TROPa.attrs['expRef'] = f'fullForcing ensemble mean'

    #co2 for MH
    years = MDR.year.values
    ifile_co2 = '/tigress/wenchang/data/cmip6/input/ghg/co2glbmean_0000-2500_ssp585.nc'
    co2 = xr.open_dataarray(ifile_co2)
    co2 = co2.sel(year=slice(years[0], years[-1]))#only keep years overlaped with MDR/TROP
    logco2a = np.log(co2/co2.sel(year=1990))
    co2.attrs['source'] = ifile_co2

    #MH (major hurricane #)
    MH = np.exp(-0.01678 + 2.19472*MDRa - 1.79117*TROPa - 0.38783*logco2a)
    MH.attrs['long_name'] = 'MH#: EXP(-0.01678 + 2.19472*MDRa - 1.79117*TROPa - 0.38783*logco2a)'
    if yearsRef:
        MH.attrs['yearsRef'] = f'{yearsRef.start}-{yearsRef.stop}'
    if fullForcingRef:
        MH.attrs['expRef'] = f'fullForcing ensemble mean'

    #MH (major hurricane #) without using CO2
    MHnoCO2 = np.exp(-0.01678 + 2.19472*MDRa - 1.79117*TROPa)# - 0.38783*logco2a)
    MHnoCO2.attrs['long_name'] = 'MH#: EXP(-0.01678 + 2.19472*MDRa - 1.79117*TROPa)'# - 0.38783*logco2a)'
    if yearsRef:
        MHnoCO2.attrs['yearsRef'] = f'{yearsRef.start}-{yearsRef.stop}'
    if fullForcingRef:
        MHnoCO2.attrs['expRef'] = f'fullForcing ensemble mean'

    #HU (hurricane #)
    HU = np.exp(1.707 + 1.388*MDRa - 1.521*TROPa)
    HU.attrs['long_name'] = 'HU#: EXP(1.707 + 1.388*MDRa - 1.521*TROPa)'
    if yearsRef:
        HU.attrs['yearsRef'] = f'{yearsRef.start}-{yearsRef.stop}'
    if fullForcingRef:
        HU.attrs['expRef'] = f'fullForcing ensemble mean'

    #TS (tropical storm #)
    TS = np.exp(2.10356 + 0.97612*MDRa - 0.97102*TROPa)
    TS.attrs['long_name'] = 'TS#: EXP(2.10356 + 0.97612*MDRa - 0.97102*TROPa)'
    if yearsRef:
        TS.attrs['yearsRef'] = f'{yearsRef.start}-{yearsRef.stop}'
    if fullForcingRef:
        HU.attrs['expRef'] = f'fullForcing ensemble mean'

    #PDI
    PDI = np.exp(0.76 + 1.87*MDRa - 1.58*TROPa)
    PDI.attrs['long_name'] = 'PDI: EXP(0.76 + 1.87*MDRa - 1.58*TROPa)'
    if yearsRef:
        PDI.attrs['yearsRef'] = f'{yearsRef.start}-{yearsRef.stop}'
    if fullForcingRef:
        HU.attrs['expRef'] = f'fullForcing ensemble mean'

    # output dataset
    ds_o = xr.Dataset(dict(
        MH=MH, MHnoCO2=MHnoCO2, HU=HU, TS=TS, PDI=PDI, MDR=MDR, MDRa=MDRa, TROP=TROP, TROPa=TROPa, co2=co2))

    # save to nc file
    if ofile and os.path.exists(ofile):
        print('[exists]:', ofile)
    if ofile and not os.path.exists(ofile):
        encoding = {v:{'_FillValue': None, 'dtype': 'float32'} 
            for v in ['MH', 'MHnoCO2', 'HU', 'TS', 'PDI', 'MDR', 'MDRa', 'TROP', 'TROPa', 'co2']}
        encoding['year'] = {'_FillValue': None, 'dtype': 'int32'}
        print('loading...')
        ds_o.load()
        print('saving...')
        ds_o.to_netcdf(ofile, encoding=encoding)
        print('[saved]:', ofile)

    return ds_o
     
if __name__ == '__main__':
    #from wyconfig import * #my plot settings
    """
    ifiles = 'LME_SST/b.e11.B1850C5CN.f19_g16.0850cntl.001.*.nc'
    ofile = 'LME_TC.0850cntl.nc'
    yearsRef = slice(1901, 2000) # reference years in calculation of sst anomaly for TC indices

    sst_to_vecchi_indices(ifiles, ofile, yearsRef=yearsRef)
    """
    
    #savefig
    if len(sys.argv)>1 and 'savefig' in sys.argv[1:]:
        figname = __file__.replace('.py', f'.png')
        if 'overwritefig' in sys.argv[1:]:
            wysavefig(figname, overwritefig=True)
        else:
            wysavefig(figname)
    tt.check(f'**Done**')
    plt.show()
    
