#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Fri Dec 31 11:54:45 EST 2021
if __name__ == '__main__':
    import sys
    from misc.timer import Timer
    s = ' '
    tt = Timer(f'start {s.join(sys.argv)}')
import sys, os.path, os, glob, datetime
import xarray as xr, numpy as np, pandas as pd, matplotlib.pyplot as plt
#more imports
import cartopy.crs as ccrs
#from data.Lizzie.wyplot_map_sites import wyplot as plot_sites
#from data.Lizzie.wyplot_ages import wyplot as plot_ages
#from fig_lines_sedimentHUcount import wyplot as plot_lines_sedimentHUcount
from fig_map_ssta import wyplot as plot_map_ssta
from fig_lines_lmrMDRtrop import wyplot as plot_lines_lmrMDRtrop
from fig_lines_lmrHU import wyplot as plot_lines_lmrHU
from shared import axlabel, axscale
#
if __name__ == '__main__':
    tt.check('end import')
#
#start from here
 
 
if __name__ == '__main__':
    from wyconfig import * #my plot settings
    #constrained_layout_off()
    proj = ccrs.Robinson(central_longitude=180)
    dproj = ccrs.PlateCarree()
    plt.close()
    #fig, axes = plt.subplots(3, 2, figsize=(8*2,9), dpi=80)
    #fig = plt.figure(figsize=((4+8)*1.05, 6*1.1), dpi=100)
    fig = plt.figure(figsize=(8, 9), dpi=100)
    nrows, ncols = 3, 2
    gs = fig.add_gridspec(nrows=nrows, ncols=ncols)
    axes = []

    #ssta lmr2018
    ax = fig.add_subplot(gs[0, 0], projection=proj)
    im = plot_map_ssta(ax=ax, lmr='2018', add_colorbar=False)
    ax.set_title('LMR2.0', loc='center')
    axes.append(ax)

    #ssta lmr2019
    ax = fig.add_subplot(gs[0, 1], projection=proj)
    im = plot_map_ssta(ax=ax, lmr='2019', add_colorbar=False)
    ax.set_title('LMR2.1', loc='center')
    axes.append(ax)

    fig.colorbar(im, ax=axes, label='0850-1850 SST anomaly from 1901-2000 [K]', orientation='horizontal', shrink=0.5)

    #mdr/trop
    ax = fig.add_subplot(gs[1,0:ncols])
    plot_lines_lmrMDRtrop(ax=ax)
    axes.append(ax)


    #hu
    ax = fig.add_subplot(gs[2,0:ncols])
    plot_lines_lmrHU(ax=ax)
    axes.append(ax)

    
    """
    for ax in axes[-3:-1]: ax.set_xlabel('')
    for ax,label in zip(axes[0:2], list('AB')): axlabel(ax, label, x=-0.12, y=1.02)
    for ax,label in zip(axes[2:], list('CDE')): axlabel(ax, label, x=-0.05, y=1.05)
    #axscale(axes[0,0], left=0.3, right=0.3, up=0.3, down=0.3)
    #axscale(axes[2,0], up=0.5)
    """
    for ax,label in zip(axes, list('ABCD')): axlabel(ax, label, x=-0.02, y=1.05)
    axes[2].set_xlabel('')
    
    #savefig
    if len(sys.argv)>1 and 'savefig' in sys.argv[1:] or 's' in sys.argv:
        figname = __file__.replace('.py', f'.png')
        if 'pdf' in sys.argv: figname = figname.replace('.png', '.pdf')
        if 'overwritefig' in sys.argv[1:] or 'o' in sys.argv[1:]:
            wysavefig(figname, overwritefig=True)
        else:
            wysavefig(figname)
    tt.check(f'**Done**')
    plt.show()
    #constrained_layout_on()
    
