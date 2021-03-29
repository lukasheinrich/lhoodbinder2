# JSON Likelihoods for ATLAS SUSY sbottom multi-b analysis

The JSON likelihoods are serialized for each signal region: [RegionA](RegionA), [RegionB](RegionB), and [RegionC](RegionC). This is done by providing a background-only workspace containing the signal/control/validation channels for each region at `$region/BkgOnly.json` as well as patch files for each mass point on the signal phase-space explored in the analysis.

Each [jsonpatch](http://jsonpatch.com/) file follows the format `$region/patch.sbottom_msb_mn2_mn1.json` where `msb` is the mass of the sbottom squark, `mn2` is the mass of the second-lightest neutralino, and `mn1` is the mass of the lightest supersymmetric particle (LSP).

This particular analysis has two mass scenarios. In the [associated PUB note](https://atlas.web.cern.ch/Atlas/GROUPS/PHYSICS/PUBNOTES/ATL-PHYS-PUB-2019-029/), the reproduction of `mn1 = 60 GeV` is shown. The other mass scenario is where `mn2 - mn1 = 130 GeV`. To get files for each mass scenario, you can use bash like so:

```
find . -name "patch.sbottom*.json" | awk -F_ '$3-$4==130 {print $0}'
find . -name "patch.sbottom*.json" | awk -F_ '$4==60 {print $0}'
```

## Producing signal workspaces

As an example, we use [python jsonpatch](https://python-json-patch.readthedocs.io/en/latest/) here:

```
jsonpatch RegionA/BkgOnly.json RegionA/patch.sbottom_1300_850_60.json > RegionA/sbottom_1300_850_60.json
```

## Computing signal workspaces

For example, with [pyhf](https://diana-hep.org/pyhf/), you can do any of the following:

```
pyhf cls RegionA/BkgOnly.json -p RegionA/patch.sbottom_1300_850_60.json

jsonpatch RegionA/BkgOnly.json RegionA/patch.sbottom_1300_850_60.json | pyhf cls

pyhf cls RegionA/sbottom_1300_850_60.json
```
