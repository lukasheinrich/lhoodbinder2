import re
import json
import glob
import subprocess
import shlex
from collections import namedtuple
from multiplex import main as multiplex_main
from interpolate import main as interpolate_main
import numpy as np
from shapely.geometry.polygon import Polygon
from descartes import PolygonPatch

pattern = re.compile("sbottom_(\d+)_(\d+)_(\d+)")
def make_harvest_from_result(key,result):
    m = pattern.search(key)
    masses = list(map(int, m.groups()))
    return {
        "CLs": result["CLs_obs"],
        "CLsexp": result["CLs_exp"][2],
        "clsd1s": result["CLs_exp"][1],
        "clsd2s": result["CLs_exp"][0],
        "clsu1s": result["CLs_exp"][3],
        "clsu2s": result["CLs_exp"][4],
        "failedstatus": 0,
        "mn1": masses[2],
        "mn2": masses[1],
        "msb": masses[0],
        "upperLimit": -1,
        "expectedUpperLimit": -1,
    }
    
def harvest_results(regions):

    dataList = []
    for region in regions:
        harvest = []
        files = "results/region{region}.result.sbottom_*_*_*.json".format(
            region = region,
        )
        for fname in glob.glob(files):
            result = json.load(open(fname))
            this_harvest =      (fname,result)

            if this_harvest['mn1'] != 60:
                continue
            harvest.append(this_harvest)
        dataList.append(
            ('region{}'.format(region),harvest)
        )
    return dataList


def make_interpolated_results(dataList):
    if not (dataList[0][1] or dataList[1][1]):
        return None,None

    d = {
        'figureOfMerit': 'CLsexp',
        'modelDef': 'msb,mn2,mn1',
        'ignoreTheory': True,
        'ignoreUL': True,
        'debug': False,
    }
    args = namedtuple('Args',d.keys())(**d)
    mux_data = multiplex_main(args,
        inputDataList =  dataList,

    ).to_dict(orient = "records")
    
    d = {
        'nominalLabel': 'Nominal',
        'xMin': None,
        'xMax': None,
        'yMin': None,
        'yMax': None,
        'smoothing': '0.1',
        'areaThreshold': 0,
        'xResolution': 100,
        'yResolution': 100,
        'xVariable': 'msb',
        'yVariable': 'mn2',
        'closedBands': False,
        'forbiddenFunction': 'x',
        'debug': False,
        'logX': False,
        'logY': False,
        'noSig': False,
        'interpolation': 'multiquadric',
        'interpolationEpsilon': 0,
        'level': 1.64485362695,
        'useROOT': False,
        'sigmax': 5,
        'useUpperLimit': False,
        'ignoreUncertainty': False,
        'fixedParamsFile': ''
    }
    args = namedtuple('Args',d.keys())(**d)
    r = interpolate_main(args,mux_data)
    return r,dataList

def make_plot(ax, dataList, **kwargs):
    ax.cla()
    ax.set_xlim(300,1700)
    ax.set_ylim(198,1700)

    if kwargs.get('showPoints',False):
        y = np.asarray([[xx['msb'],xx['mn2']] for xx in dataList[0][1]])
        ax.scatter(y[:,0],y[:,1], s = 20, alpha = 0.2)
        y = np.asarray([[xx['msb'],xx['mn2']] for xx in dataList[1][1]])
        ax.scatter(y[:,0],y[:,1], s = 10, alpha = 0.2)


    if kwargs.get('showInterPolated',False):
        r,x = make_interpolated_results(dataList)
        if r is None:
            return

        if not 'Band_1s_0' in r:
            return


        x = r['Band_1s_0'][:,0]
        y = r['Band_1s_0'][:,1]
        
        explabel = r'Expected Limit ($\pm1\sigma$)'
        p = ax.add_patch(
            PolygonPatch(Polygon(np.stack([x,y]).T),alpha = 0.5, facecolor = kwargs.get('color','steelblue'),label = explabel),
        )


        x = r['Exp_0'][:,0]
        y = r['Exp_0'][:,1]
        ax.plot(x,y,  color = 'k', linestyle = 'dashed', alpha = 0.5)

        x = r['Obs_0'][:,0]
        y = r['Obs_0'][:,1]

        ax.plot(x,y,  color = 'maroon', linewidth = 2, linestyle = 'solid', alpha = 0.5, label = 'Observed Limit')

    apply_decorations(ax,kwargs['label'])
    
def apply_decorations(ax,label):
    ax.set_xlim(300,1700)
    ax.set_ylim(200,1700)
    # dictionaries to hold the styles for re-use
    text_fd = dict(ha='left', va='center')
    atlas_fd = dict(weight='bold', style='italic', size=24, **text_fd)
    internal_fd = dict(size=24, **text_fd)

    # actually drawing the text
    ax.text(0.05,0.9,'ATLAS', fontdict=atlas_fd, transform=ax.transAxes)
    ax.text(0.23,0.9,label, fontdict=internal_fd, transform=ax.transAxes)

    ax.text(
        0.05,
        0.8,
        "$\sqrt{s} = 13\ \mathrm{TeV}, 139\ \mathrm{fb}^{-1}$\n All limits at 95% CL",
        fontdict=text_fd,
        transform=ax.transAxes
    )
    ax.text(
        0.0,
        1.035,
        r"$\tilde{b}_1\tilde{b}_1$ production ; $\tilde{b}_1\to b \tilde{\chi}_2^0$; $m(\tilde{\chi}_1^0)$ = 60 GeV",
        fontdict=text_fd,
        transform=ax.transAxes
    )
    

    ax.text(
        350,
        750,
        r"Kinematically Forbidden $m(\tilde{\chi}_2^0)>m(\tilde{b}_1)$",
        rotation = 35.0,
        fontdict=dict(ha='left', va='center', size = 15, color = 'grey'),
    )
    ax.set_xlabel(r'$m(\tilde{b}_1)$ [GeV]',fontdict=dict(ha='right', va='center', size = 20))
    ax.set_ylabel(r'$m(\tilde{\chi}_2^0)$ [GeV]',fontdict=dict(ha='right', va='center', size = 20))
    
    ax.legend(loc = (0.05,0.6))
    ax.xaxis.set_label_coords(1.0, -0.1)
    ax.yaxis.set_label_coords(-0.15, 1.0)
    ax.plot([200,1400],[200,1400],color = 'grey', linestyle = 'dashdot')

if __name__ == '__main__':
    main()