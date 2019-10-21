import re
import json
import glob
import subprocess
import shlex

def make_harvest_from_result(result, masses):
    return {
        "CLs": result["CLs_obs"],
        "CLsexp": result["CLs_exp"][2],
        "clsd1s": result["CLs_exp"][1],
        "clsd2s": result["CLs_exp"][0],
        "clsu1s": result["CLs_exp"][3],
        "clsu2s": result["CLs_exp"][4],
        "covqual": 3,
        "dodgycov": 0,
        "excludedXsec": -999007,
        "expectedUpperLimit": -1,
        "expectedUpperLimitMinus1Sig": -1,
        "expectedUpperLimitMinus2Sig": -1,
        "expectedUpperLimitPlus1Sig": -1,
        "expectedUpperLimitPlus2Sig": -1,
        "fID": -1,
        "failedcov": 0,
        "failedfit": 0,
        "failedp0": 0,
        "failedstatus": 0,
        "fitstatus": 0,
        "mn1": masses[2],
        "mn2": masses[1],
        "mode": -1,
        "msb": masses[0],
        "nexp": -1,
        "nofit": 0,
        "p0": 0,
        "p0d1s": -1,
        "p0d2s": -1,
        "p0exp": -1,
        "p0u1s": -1,
        "p0u2s": -1,
        "p1": 0,
        "seed": 0,
        "sigma0": -1,
        "sigma1": -1,
        "upperLimit": -1,
        "upperLimitEstimatedError": -1,
        "xsec": -999007,
    }
    
def harvest_results(regions):
    pattern = re.compile("sbottom_(\d+)_(\d+)_(\d+)")

    dataList = []
    for region in regions:
        harvest = []
        files = "results/region{region}.result.sbottom_*_*_*.json".format(
            region = region,
        )
        for fname in glob.glob(files):
            result = json.load(open(fname))
            m = pattern.search(fname)
            masses = list(map(int, m.groups()))
            # only use 60 GeV
            if masses[2] != 60:
                continue
            harvest.append(make_harvest_from_result(result, masses))
        dataList.append(
            ('region{}'.format(region),harvest)
        )
    return dataList


def plotit(
    band,
    expected,
    observed,
    width = 1600,
    height = 1200,
    comenergy = "13 TeV",
    lumilabel = "#sqrt{{s}} = {comEnergy}, {luminosity} fb^{{-1}}",
    xlabel = "m(#tilde{b}_{1}) [GeV]",
    ylabel = "m(#tilde{#chi}^{0}_{2}) [GeV]",
    xmin = 300,
    xmax = 1700,
    ymin = 198,
    ymax = 1700,
    is_internal = False,
    is_preliminary = False,
    labels_left = 0.2,
    labels_top = 0.86,
    process_label = "#tilde{b}_{1} #tilde{b}_{1}  production ; #tilde{b}_{1} #rightarrow b #tilde{#chi}_{2}^{0} #rightarrow b h #tilde{#chi}_{0}^{1} ; m(#tilde{#chi}_{1}^{0}) = 60 GeV",
    luminosity = 139000,
):
    import os
    import contourPlotter
    import math
    import ROOT

    ROOT.PyConfig.IgnoreCommandLineOptions = True
    ROOT.gROOT.SetBatch(True)
    ROOT.gStyle.SetOptStat(0000)
    ROOT.gStyle.SetOptTitle(0)

    plot = contourPlotter.contourPlotter(
        "multiplex_contour", width, height
    )
    plot.canvas.SetLeftMargin(0.15)


    ## Axes
    plot.drawAxes([xmin, ymin, xmax, ymax])

    ## Other limits to draw
    # plot.drawShadedRegion( externalGraphs.curve, title="ATLAS 8 TeV, 20.3 fb^{-1} (observed)" )

    plot.drawOneSigmaBand(band)
    plot.drawExpected(expected)
    plot.drawObserved(observed, title="Observed Limit")

    ## Draw Lines
    plot.drawLine(
        coordinates=[300, 300, 1500, 1500],
        label="Kinematically Forbidden m(#tilde{#chi}_{2}^{0}) > m(#tilde{b}_{1})",
        style=8,
        angle=38,
        color=ROOT.kGray + 1,
        labelLocation=[350, 450],
    )

    ## Axis Labels
    plot.setXAxisLabel(xlabel)
    plot.setYAxisLabel(ylabel)
    plot.bottomObject.GetXaxis().SetTitleSize(0.04)
    plot.bottomObject.GetXaxis().SetLabelSize(0.04)
    plot.bottomObject.GetYaxis().SetTitleSize(0.04)
    plot.bottomObject.GetYaxis().SetLabelSize(0.04)

    # legend = plot.createLegend(shape=(0.55,0.8,0.8,labels_top+0.04) )
    # plot.createLegend(shape=(0.22,0.58,0.55,0.77) ).Draw()
    legend = plot.createLegend(
        shape=(
            labels_left - 0.01,
            labels_top - 0.09,
            labels_left + 0.3,
            labels_top - 0.17,
        )
    )
    legend.SetTextSize(0.035)
    legend.Draw()

    plot.canvas.cd()
    latexObject = ROOT.TLatex()
    latexObject.SetTextFont(42)
    latexObject.SetTextAlign(11)
    latexObject.SetTextColor(1)

    latexObject.SetTextSize(0.035)
    latexObject.DrawLatexNDC(0.16, 0.95, process_label)

    latexObject.SetTextSize(0.037)
    latexObject.DrawLatexNDC(
        labels_left,
        labels_top - 0.04,
        lumilabel.format(comEnergy=comenergy, luminosity=luminosity / 1.0e3),
    )
    latexObject.DrawLatexNDC(
        labels_left, labels_top - 0.04 * 2, "All limits at 95% CL"
    )

    latexObject.SetTextSize(0.041)
    if is_internal:
        latexObject.DrawLatexNDC(
            labels_left, labels_top, "#scale[1.2]{#bf{#it{ATLAS}} Internal}"
        )
    elif is_preliminary:
        latexObject.DrawLatexNDC(
            labels_left, labels_top, "#scale[1.2]{#bf{#it{ATLAS}} Preliminary}"
        )
    else:
        latexObject.DrawLatexNDC(
            labels_left, labels_top, "#scale[1.2]{#bf{#it{ATLAS}}}"
        )

    ROOT.gPad.RedrawAxis()
    plot.canvas.SetTicks()
    plot.canvas.Update()

def main():
    harvest_results()
    subprocess.call(shlex.split('multiplexJSON.py -i results/harvest.RegionA.json results/harvest.RegionA.json  --modelDef msb,mn2,mn1 -o results/multiplex.json'))
    plotit()

if __name__ == '__main__':
    main()