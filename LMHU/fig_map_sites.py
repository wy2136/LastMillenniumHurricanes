#!/usr/bin/env python
# Wenchang Yang (wenchang@princeton.edu)
# Thu Aug 18 10:58:14 EDT 2022
if __name__ == '__main__':
    import sys
    from misc.timer import Timer
    tt = Timer('start ' + ' '.join(sys.argv))
import sys, os.path, os, glob, datetime
import xarray as xr, numpy as np, pandas as pd, matplotlib.pyplot as plt
#more imports
from misc.wysalem import get_world_shape
from geoplots import xticks2lon, yticks2lat
from misc.shell import run_shell
#
if __name__ == '__main__':
    tt.check('end import')
#
#start from here
shdf = get_world_shape()
"""
#colors from Lizzie
jk_color_list = [
    [166,206,227],
    [31,120,180], 
    [178,223,138],
    [51,160,44],
    [251,154,153],
    [227,26,28],
    [253,191,111],
    [255,127,0],
    [202,178,214],
    [106,61,154],
    [255,255,153],
    [177,89,40],
    [150,150,150],
    ]
jk_color_list = np.array(jk_color_list)/256
"""
jk_color_list = plt.get_cmap('tab20')(np.linspace(0,1,20))
ifile = '/tigress/wenchang/analysis/LMHU/data/Lizzie/raw/age_site_info/site_locations.csv'
ifile_cached = __file__.replace('.py', '.csv')
if not os.path.exists(ifile_cached): run_shell(f'cp {ifile} {ifile_cached}')
#df = pd.read_csv(ifile)
df = pd.read_csv(ifile_cached)
print('[loaded]:', ifile_cached)
df_ = df.iloc[0:-1, :] #remove the last site Cay Sal
print(df_)

def wyplot(ax=None):
    if ax is None:
        fig,ax = plt.subplots(figsize=(5,4))
    shdf.plot(ax=ax, color='0.8')
    for ii,row in df_.iterrows():
        lon = row['Longitude']
        lat = row['Latitude']
        ireg = row['Region number']
        #print(ireg, lon, lat)
        ax.plot(lon, lat, marker='$*$', markersize=10, color=jk_color_list[ireg-1])
        #ax.text(lon, lat, str(ireg))

    ax.set_xlim(-90,-60)
    ax.set_ylim(15,45)
    xticks2lon(range(-90,-59, 5), ax=ax)
    yticks2lat(range(15,46,5), ax=ax)
    ax.set_title('locations of sites')
 
if __name__ == '__main__':
    from wyconfig import * #my plot settings
    wyplot()

    
    #savefig
    if 'savefig' in sys.argv or 's' in sys.argv:
        figname = __file__.replace('.py', f'.png')
        if 'overwritefig' in sys.argv or 'o' in sys.argv:
            wysavefig(figname, overwritefig=True)
        else:
            wysavefig(figname)
    tt.check(f'**Done**')
    print()
    if 'notshowfig' in sys.argv:
        pass
    else:
        plt.show()
    
