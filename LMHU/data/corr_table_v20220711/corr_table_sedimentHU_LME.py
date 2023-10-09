#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Fri Dec 31 12:49:58 EST 2021
if __name__ == '__main__':
    import sys
    from misc.timer import Timer
    s = ' '
    tt = Timer(f'start {s.join(sys.argv)}')
import sys, os.path, os, glob, datetime
import xarray as xr, numpy as np, pandas as pd, matplotlib.pyplot as plt
#more imports
import xlinregress
import xfilter
import xpyleoclim
#
if __name__ == '__main__':
    tt.check('end import')
#
#start from here
#params from sys.argv
daname = 'MH' if len(sys.argv)>1 and 'MH' in sys.argv[1:] else 'HU'
wCaySal = True if len(sys.argv)>1 and 'wCaySal' in sys.argv[1:] else False
noCaySal_noCaicos = True if len(sys.argv)>1 and 'noCaySal_noCaicos' in sys.argv[1:] else False
pyleoclim = True if len(sys.argv)>1 and 'pyleoclim' in sys.argv[1:] else False
year_stop = 2000 if len(sys.argv)>1 and '2000' in sys.argv[1:] else 1850
#use_max = True if 'max' in sys.argv else False
sediMethod = 'median'
if 'max' in sys.argv:
    sediMethod = 'max'
elif 'wymax' in sys.argv:
    sediMethod = 'wymax'
elif 'wymedian' in sys.argv:
    sediMethod = 'wymedian'

n_window = 40 #cutoff for lowpass
lowpass = lambda da: da.filter.lowpass(1/n_window, dim='year', padtype='even')
years = slice(850,year_stop)
ofile = f'corr_table_sedimentHUnoCaySal_vs_lme{daname}_{years.start}-{years.stop}.nc'
if wCaySal:
    ofile = ofile.replace('noCaySal', 'wCaySal')
elif noCaySal_noCaicos:
    ofile = ofile.replace('noCaySal', 'noCaySal_noCaicos')
#if use_max:
if sediMethod == 'max':
    ofile = ofile.replace('sediment', 'sedimentMax')
elif sediMethod == 'wymax':
    ofile = ofile.replace('sediment', 'sedimentMaxWy')
elif sediMethod == 'wymedian':
    ofile = ofile.replace('sediment', 'sedimentMedianWy')
#elif daname == 'MH':
#    ofile = ofile.replace('HUnoCaySal', 'MH')
if pyleoclim:
    ofile = ofile.replace('.nc', '_pyleoclim.nc')
if os.path.exists(ofile):
    ds = xr.open_dataset(ofile)
    print('[loaded]:', ofile)
else:
    #sediment HU
    ifile = '../Lizzie/sedimentHU_v20220711_noCaySal_smooth40yr_count.nc'
    #if use_max:
    if sediMethod == 'max':
        ifile = ifile.replace('v20220711', 'v20220711max')
    elif sediMethod == 'wymax':
        #ifile = '../Lizzie/sedimentHU_v20220711ens_noCaySal_wy_max_lp40.nc'
        ifile = ifile.replace('v20220711', 'v20220711ens').replace('smooth40yr', 'wy_max_lp40')
    elif sediMethod == 'wymedian':
        #ifile = '../Lizzie/sedimentHU_v20220711ens_noCaySal_wy_median_lp40.nc'
        ifile = ifile.replace('v20220711', 'v20220711ens').replace('smooth40yr', 'wy_median_lp40')
    if wCaySal:
        ifile = ifile.replace('noCaySal', 'wCaySal')
    elif noCaySal_noCaicos:
        ifile = ifile.replace('noCaySal', 'noCaySal_noCaicos')
    #elif daname == 'MH':
    #    ifile = ifile.replace('_noCaySal_', '_').replace('HU', 'MH')
    ds_liz = xr.open_dataset(ifile)
    #LME HU
    ifile = '../LME/LME_sstTC_fullForcing_13ens.nc'
    ds_lme = xr.open_dataset(ifile)
    #sediment HU
    da = ds_liz['sedimentHUcount'].sel(year=years) #
    da_liz = xr.concat([da.isel(member=slice(0,1)), da.isel(member=slice(3,None))], dim='member') #remove lower/upper estimates
    members = da_liz.member.values
    members[0] = 'allSites' # sediment_estimate -> allSites
    da_liz = da_liz.assign_coords(member=members)
    #LME HU
    da = ds_lme[daname]
    da_lme = xr.concat([da.mean('ens'), da.drop('ens')], dim='ens').assign_coords(ens=['em',]+list(range(1, da.ens.size+1))) #add ensemble mean to the first
    da_lme = da_lme.pipe(lowpass).sel(year=years) #lowpass
    if pyleoclim:
        result = xpyleoclim.correlation(da_liz, da_lme, seed=0)
        ds = result[['r', 'p', 'signif']].rename(p='pvalue')
    else:
        rg = da_liz.linregress.on(da_lme, dim='year', ess_on=True)
        ds = rg[['r', 'dof', 'pvalue']]
    ds.to_netcdf(ofile)
    print('[saved]:', ofile)
 
if __name__ == '__main__':
    from wyconfig import * #my plot settings
    plt.close()
    figsize = (8,4)
    fig, ax = plt.subplots(figsize=figsize)
    one_tailed = True
    alpha = 0.1
    da = ds.r
    p = ds.pvalue
    da.drop(['member', 'ens']).plot(ax=ax, vmax=1, cmap='RdBu_r') 
    
    #add corr info to the plot; significant values are black
    for ii in range(da.member.size):
        for jj in range(da.ens.size):
            rr = da.isel(member=ii, ens=jj).item()
            pp = p.isel(member=ii, ens=jj).item()
            color = 'k' if pp<alpha else 'gray'
            if one_tailed:
                color = 'k' if pp<alpha*2 and rr>0 else 'gray'
            ax.text(jj, ii, f'{rr*100:2.0f}', ha='center', va='center', color=color)
    ax.set_yticks(range(da.member.size))
    ax.set_yticklabels(da.member.values)
    ax.set_xticks(range(da.ens.size))
    ax.set_xticklabels(da.ens.values)
    ax.set_xlabel('')
    ax.set_ylabel('')
    title = ' '.join( os.path.splitext(ofile)[0].split('_') )
    if alpha > 0.05:
        title += f' alpha={alpha}'
    if one_tailed:
        title += ' one-tailed'
    ax.set_title(title)

    
    #savefig
    if len(sys.argv)>1 and 'savefig' in sys.argv[1:]:
        #figname = __file__.replace('.py', f'.png')
        figname = ofile.replace('.nc', '.png')
        if alpha > 0.05:
            figname = figname.replace('.png', f'_alpha{int(alpha*100)}.png')
        if one_tailed:
            figname = figname.replace('.png', '_onetailed.png')
        if 'overwritefig' in sys.argv[1:]:
            wysavefig(figname, overwritefig=True)
        else:
            wysavefig(figname)
    tt.check(f'**Done**')
    plt.show()

