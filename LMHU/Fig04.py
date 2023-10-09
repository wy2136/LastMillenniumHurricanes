#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Mon Jan 10 16:46:23 EST 2022
if __name__ == '__main__':
    import sys
    from misc.timer import Timer
    tt = Timer('start ' + ' '.join(sys.argv))
import sys, os.path, os, glob, datetime
import xarray as xr, numpy as np, pandas as pd, matplotlib.pyplot as plt
#more imports
from shared import axlabel
from fig_lines_lmeHU import wyplot as plot_lines_lmeHU
from fig_lines_LMErMDRa import wyplot as plot_lines_LMErMDRa
from fig_lines_lmeTROPa import wyplot as plot_lines_lmeTROPa
#
if __name__ == '__main__':
    tt.check('end import')
#
#start from here
 
 
if __name__ == '__main__':
    from wyconfig import * #my plot settings
    fig, axes = plt.subplots(3, 1, figsize=(8,8))
    ax = axes[0]
    plot_lines_lmeHU(ax=ax)
    ax.set_yticks(range(3,16,2))

    ax = axes[1]
    plot_lines_LMErMDRa(ax=ax)

    ax = axes[2]
    plot_lines_lmeTROPa(ax=ax)

    for ax,label in zip(axes, list('ABC')):
        axlabel(ax=ax, label=label, x=-0.1, y=1.03)
    for ax in axes[:-1]:
        ax.set_xlabel('')
    
    #savefig
    if len(sys.argv)>1 and 'savefig' in sys.argv[1:] or 's' in sys.argv:
        figname = __file__.replace('.py', f'.png')
        if 'pdf' in sys.argv: figname = figname.replace('.png', '.pdf')
        if 'overwritefig' in sys.argv[1:] or 'o' in sys.argv:
            wysavefig(figname, overwritefig=True)
        else:
            wysavefig(figname)
    tt.check(f'**Done**')
    plt.show()
    
