#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Wed Dec 18 23:32:43 EST 2019
import sys, os.path, os, datetime
import xarray as xr, numpy as np, pandas as pd
#import matplotlib.pyplot as plt
#pr nt()
# vecchi indices based on sst on regular lon/lat grids

#ifile = 'LMR_2018/sst_MCruns_ensemble_mean.nc'
#ofile = 'LMR2018_TC.nc'
#ifile = 'LMR_2019/sst_MCruns_ensemble_mean.nc'
#ofile = 'LMR2019_TC.nc'
#ifiles = ['LMR_2018/sst_MCruns_ensemble_mean.nc', 'LMR_2019/sst_MCruns_ensemble_mean.nc']
ifiles = ['/tigress/gvecchi/DATA/LMR_2018/sst_MCruns_ensemble_mean.nc',
    '/tigress/gvecchi/DATA/LMR_2019/sst_MCruns_ensemble_mean.nc']
ofiles = ['LMR2018TC.nc', 'LMR2019TC.nc']
#ofiles = ['LMR2018_TC_noneWT.nc', 'LMR2019_TC_noneWT.nc']
#ifiles = ['CTL1860_newdiag_tigercpu_intelmpi_18_576PE/analysis/sst.0001-2000.yearly.nc',]
#ofiles = ['FLOR.CTL1860_newdiag.statmTC.0001-2000.yearly.nc',]
#sstName = 'sst'
#xName = 'lon'
#yName = 'lat'
#latName = 'lat'
#lonName = 'lon'
#areaName = None#'TAREA'
#shiftTimeAxis = False #CESM data time axis is one month late and needs a backward shift
#yearsRef = slice(1901, 2000) # reference years in calculation of sst anomaly for TC indices
def sst_to_vecchi_indices(ifile, ofile=None, sstName='sst', xName='lon', yName='lat', lonName='lon', latName='lat', areaName='coslat', shiftTimeAxis=False, yearsRef=None, constantCO2=False):
    print('[ifile]:', ifile)
    ds = xr.open_mfdataset(ifile)
    if shiftTimeAxis:
        ds['time'] = ds.indexes['time'].shift(-1, 'MS')
        print('[time shifted]:', 'one month back')
    sst = ds[sstName].squeeze()
    if 'z_t' in list(sst.coords):
        sst = sst.drop('z_t')
        print('[coords dropped]:', 'z_t')
    lon = ds[lonName]
    lat = ds[latName]
    if areaName == 'coslat':
        area = np.cos(lat*np.pi/180.0) + sst*0
    elif areaName:
        area = ds[areaName] + sst*0
    else:
        area = sst*0 + 1
        
         
    #MDR(main development region)
    inMDR = (lat>=10)&(lat<=25)&(lon>=280)&(lon<=340)
    sst_ = sst.where(inMDR)
    area_ = area.where(inMDR)
    MDR = (sst_*area_).sum([xName, yName])/area_.sum([xName, yName]) # area mean
    if 'year' not in MDR.dims:
        MDR = MDR.groupby('time.year').mean('time') # yearly mean
    MDR.attrs = sst.attrs
    MDR.attrs['long_name'] = 'MDR ' + MDR.attrs['long_name']
    if yearsRef is not None:
        MDRa = MDR - MDR.sel(year=yearsRef).mean('year')
    else:
        MDRa = MDR - MDR.mean('year')

    #TROP (tropical reagion)
    inTROP = (lat>=-30)&(lat<=30)
    sst_ = sst.where(inTROP)
    area_ = area.where(inTROP)
    TROP = (sst_*area_).sum([xName, yName])/area_.sum([xName, yName]) # area mean
    if 'year' not in TROP.dims:
        TROP = TROP.groupby('time.year').mean('time') # yearly mean
    TROP.attrs = sst.attrs
    TROP.attrs['long_name'] = 'TROP ' + TROP.attrs['long_name']
    if yearsRef is not None:
        TROPa = TROP - TROP.sel(year=yearsRef).mean('year')
    else:
        TROPa = TROP - TROP.mean('year')

    #HU (hurricane #)
    HU = np.exp(1.707 + 1.388*MDRa - 1.521*TROPa)
    HU.attrs['long_name'] = 'HU#: EXP(1.707 + 1.388*MDRa - 1.521*TROPa)'
    if yearsRef:
        HU.attrs['yearsRef'] = f'{yearsRef.start}-{yearsRef.stop}'
    
    if not constantCO2:
        #co2 for MH
        years = MDR.year.values
        co2 = xr.open_dataarray('/tigress/wenchang/data/cmip6/input/ghg/co2glbmean_0000-2500_ssp585.nc')
        co2 = co2.sel(year=slice(years[0], years[-1])) #only keep years overlaped with MDR/TROP
        logco2a = np.log(co2/co2.sel(year=1990))

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

    # output dataset
    if not constantCO2:
        ds_o = xr.Dataset(dict(
            HU=HU, MH=MH, MHnoCO2=MHnoCO2, TS=TS, PDI=PDI, MDR=MDR, TROP=TROP, co2=co2))
    else:
        ds_o = xr.Dataset(dict(
            HU=HU, MHnoCO2=MHnoCO2, TS=TS, PDI=PDI, MDR=MDR, TROP=TROP))
    

    # save to nc file
    if ofile and os.path.exists(ofile):
        print('[exists]:', ofile)
    if ofile and not os.path.exists(ofile):
        encoding = {v:{'_FillValue': None, 'dtype': 'float32'} 
            for v in ['HU', 'TS', 'PDI', 'MDR', 'TROP']}
        encoding['year'] = {'_FillValue': None, 'dtype': 'int32'}
        ds_o.to_netcdf(ofile, encoding=encoding)
        print('[saved]:', ofile)

    return ds_o
     
if __name__ == '__main__':
    tformat = '%Y-%m-%d %H:%M:%S'
    t0 = datetime.datetime.now()
    print('[start]:', t0.strftime(tformat))

    for ifile, ofile in zip(ifiles, ofiles):
        if 'noneWT' in ofile:
            areaName = None
        else:
            areaName = 'coslat'
        print(f'areaName = {areaName}')
        #sst_to_vecchi_indices(ifile, ofile, areaName=areaName, yearsRef=slice(1901,2000))
        #sst_to_vecchi_indices(ifile, ofile, areaName=areaName, yearsRef=slice(1001,2000))
        sst_to_vecchi_indices(ifile, ofile, areaName=areaName, yearsRef=slice(1979,2000), constantCO2=False)
    
    t1 = datetime.datetime.now()
    print('[total time used]:', f'{(t1-t0).seconds:,} seconds')
    print('[end]:', t1.strftime(tformat))
    print()
