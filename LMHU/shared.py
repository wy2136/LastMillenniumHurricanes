#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Mon Feb  1 14:35:02 EST 2021
if __name__ == '__main__':
    from misc.timer import Timer
    tt = Timer(f'start {__file__}')
import sys, os.path, os, glob, datetime
import xarray as xr, numpy as np, pandas as pd
#import matplotlib.pyplot as plt
#more imports
#
if __name__ == '__main__':
    tt.check('end import')
#
#start from here
def axscale(ax=None, right=0, left=0, up=0, down=0):
    '''scale the axes by the four sides'''
    if ax is None:
        ax = plt.gca()
    x0, y0, w, h = ax.get_position().bounds
    w_new = w*(1 + right + left)
    h_new = h*(1 + up + down)
    x0_new = x0 - w*left
    y0_new = y0 - h*down
    ax.set_position([x0_new, y0_new, w_new, h_new])
    return ax
def spines_off(ax):
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
def axlabel(ax, label, **kws):
    x = kws.pop('x', 0)
    y = kws.pop('y', 1)
    ha = kws.pop('ha', 'right')
    va = kws.pop('va', 'bottom')
    fontweight = kws.pop('fontweight', 'bold')
    #fontweight = kws.pop('fontweight', 'normal')
    fontsize = kws.pop('fontsize', 'large')
    ax.text(x, y, label, transform=ax.transAxes, ha=ha, va=va, fontweight=fontweight, fontsize=fontsize, **kws)

def ess_in_corr(x, y):
    '''effective sample size in correlation between x and y.
    Equation 30 in https://doi.org/10.1175/1520-0442(1999)012%3C1990:TENOSD%3E2.0.CO;2 
    '''
    N = x.size
    assert N == y.size
    
    s = 1
    for tao in range(1, N//2+1):
        rx = np.corrcoef(x[:-tao], x[tao:])[0,1]
        ry = np.corrcoef(y[:-tao], y[tao:])[0,1]
#         rx = corrcoef(x[:-tao], x[tao:])
#         ry = corrcoef(y[:-tao], y[tao:])
        if rx < 0 or ry < 0:
            break
        s+= 2*(1 - tao/N)*rx*ry
#         if tao == 1:
#             print(N*(1-rx*ry)/(1+rx*ry))
    
    return N/s 

def emulate_hu(ds, mdr, trop, yearsRef=None, lmeCase=False):
    """Compute sst-emulated hurricane frequency given dataset that includes 
    mdr and tropical mean ssts, as well as years of reference for sst anomaly.
    It looks yearsRef of 1979-2000 (1968-2000) is equivalent to 1982-2005 (1982-2010) in terms of the final results for HadISST.
    See /tigress/wenchang/analysis/TC_statmodel/wyplot_hu.py.
    """
    if yearsRef is None:
        yearsRef = slice(1979,2000)
    if lmeCase: #reference mdr/trop ssts from LME full forcing ensemble mean
        ifile = '/tigress/wenchang/analysis/LMTC/data/LME_TC.fullForcing.13ens.nc'
        ds_ref = xr.open_dataset(ifile).mean('en').load()
        ssta_mdr = ds[mdr] - ds_ref[mdr].sel(year=yearsRef).mean()
        ssta_trop = ds[trop] - ds_ref[trop].sel(year=yearsRef).mean()
    else:
        ssta_mdr = ds[mdr] - ds[mdr].sel(year=yearsRef).mean()
        ssta_trop = ds[trop] - ds[trop].sel(year=yearsRef).mean()
    hu = np.exp(1.707 + 1.388*ssta_mdr - 1.521*ssta_trop)
    hu.attrs['long_name'] = 'HU#: EXP(1.707 + 1.388*ssta_mdr - 1.521*ssta_trop)'
    hu.attrs['yearsRef'] = f'{yearsRef.start}-{yearsRef.stop}'

    return hu
 
def emulate_mh(ds, mdr, trop, yearsRef=None, lmeCase=False, co2_on=True):
    """Compute sst-emulated major hurricane frequency given dataset that includes 
    mdr and tropical mean ssts, as well as years of reference for sst anomaly.
    It looks yearsRef of 1979-2000 (1968-2000) is equivalent to 1982-2005 (1982-2010) in terms of the final results for HadISST.
    See /tigress/wenchang/analysis/TC_statmodel/wyplot_hu.py.
    """
    ifile_co2 = '/tigress/wenchang/analysis/LMTC/data/ghg_pmip3_850-2007_annual_c100517.wy.nc'
    co2 = xr.open_dataset(ifile_co2)['CO2'].load()
    logco2a = np.log(co2/co2.sel(year=1990))
    if yearsRef is None:
        yearsRef = slice(1979,2000)
    if lmeCase: #reference mdr/trop ssts from LME full forcing ensemble mean
        ifile = '/tigress/wenchang/analysis/LMTC/data/LME_TC.fullForcing.13ens.nc'
        ds_ref = xr.open_dataset(ifile).mean('en').load()
        ssta_mdr = ds[mdr] - ds_ref[mdr].sel(year=yearsRef).mean()
        ssta_trop = ds[trop] - ds_ref[trop].sel(year=yearsRef).mean()
    else:
        ssta_mdr = ds[mdr] - ds[mdr].sel(year=yearsRef).mean()
        ssta_trop = ds[trop] - ds[trop].sel(year=yearsRef).mean()
    if co2_on:
        mh = np.exp(-0.01678 + 2.19472*ssta_mdr - 1.79117*ssta_trop - 0.38783*logco2a)
        mh.attrs['long_name'] = 'MH#: EXP(-0.01678 + 2.19472*ssta_mdr - 1.79117*ssta_trop - 0.38783*logco2a)'
    else:
        mh = np.exp(-0.01678 + 2.19472*ssta_mdr - 1.79117*ssta_trop)
        mh.attrs['long_name'] = 'MH#: EXP(-0.01678 + 2.19472*ssta_mdr - 1.79117*ssta_trop)'
    mh.attrs['yearsRef'] = f'{yearsRef.start}-{yearsRef.stop}'

    return mh 

if __name__ == '__main__':
    from wyconfig import * #my plot settings
    #figname = __file__.replace('.py', f'_{tt.today()}.png')
    
    if 'figname' in locals() and figname is not None:
        plt.savefig(figname)
        print('[saved]:', figname)
    tt.check(f'**Done**')
    plt.show()
    
