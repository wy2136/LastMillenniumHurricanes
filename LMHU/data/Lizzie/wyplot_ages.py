#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Mon Aug 22 17:53:49 EDT 2022
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
ifile = '/tigress/wenchang/analysis/LMHU/data/Lizzie/raw/age_site_info/event_median_age.csv'
df = pd.read_csv(ifile)
print('sites long names:', df.columns)
df = df.rename(columns={
    'New England': 'NewEng',
    'Mid Atlantic': 'MidAtl',
    'Southeast': 'Southeast',
    'Gulf Apalachee Bay':'GulfApaBay',
    'Gulf Choctawhatchee Bay': 'GulfChoBay',
    'Abaco & Grand Bahamas': 'Abaco',
    'Andros Island': 'AndrosAM4',
    'Long Island, Bahamas': 'LIBHBahamas',
    'Middle Caicos': 'MidCaicos',
    'Vieques PR': 'VieqPR',
    'Yucatan': 'Yucatan',
    'Lighthouse Reef Belize': 'LRBHBelize',
    'Cay Sal': 'CaySal',
    })
print('sites short names:', df.columns)
df_ = df.iloc[:, 0:-1] #remove the last col Cay Sal
print(df_)
nyears, ncols = df_.shape
jk_color_list = plt.get_cmap('tab20')(np.linspace(0,1,20))
 
def wyplot(ax=None): 
    if ax is None:
        fig,ax = plt.subplots()
    for ii in range(ncols):
        xx = df_.iloc[:, ii]
        xx = xx.where((xx>=850)&(xx<=2000))
        yy = (ncols - ii)*np.ones(nyears)
        ax.scatter(xx, yy, color=jk_color_list[ii], s=10)

    ax.set_yticks(range(1,ncols+1))
    ax.set_yticklabels(df_.columns[-1::-1])
    ax.set_xlim(850, 2000)
    ax.set_xticks(range(2000, 850, -100))
    ax.set_xlabel('year')
    ax.set_title('Event median ages')

if __name__ == '__main__':
    from wyconfig import * #my plot settings
    wyplot()
    
    #savefig
    if len(sys.argv)>1 and 'savefig' in sys.argv[1:] or 's' in sys.argv:
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
    
