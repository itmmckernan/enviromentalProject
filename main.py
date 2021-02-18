import pandas as pd
from scipy.spatial import KDTree
import plotly.express as px
import plotly.subplots as sp
import math

# test for a commit

powerPlants = pd.read_csv(open('./dataFiles/global_power_plant_database.csv', encoding='utf-8'))
cancerRates = pd.read_csv(open('dataFiles/incd_all.csv', encoding='utf-8'))
countyCenters = pd.read_csv(open('./dataFiles/county_centers.csv', encoding='utf-8'))

plantTypes = ['Wind', 'Coal', 'Gas', 'Hydro', 'Oil', 'Biomass', 'Waste']
cancerMerged = cancerRates.merge(countyCenters, on="fips", how='right')
pollutionRateByCounty = {}
subPowerPlants = {}
subTrees = {}
for plantType in plantTypes:
    subPowerPlants[plantType] = powerPlants.query("primary_fuel == '{}'".format(plantType))
    subTrees[plantType] = KDTree(subPowerPlants[plantType][['latitude', 'longitude']].values)

for county in cancerMerged.iterrows():
    print(county[0])
    if math.isnan(county[1]['pclon10']):
        coords = [county[1]['pclon00'], county[1]['pclat00']]
    else:
        coords = [county[1]['pclon10'], county[1]['pclat10']]
    pollutionRateByCounty[county[1]['fips']] = {}
    for plantType in plantTypes:
        treeResults = subTrees[plantType].query(x=coords, k=15)
        pollutionRateByCounty[county[1]['fips']][plantType] = 0
        for treeResult in zip(treeResults[0], treeResults[1]):
            result = subPowerPlants[plantType].iloc[treeResult[1]]
            pollutionRateByCounty[county[1]['fips']][plantType] += result['capacity_mw'] / math.pow(treeResult[0], 2)

#make coords
cancerMerged['coords'] = [cancerMerged['pclon00'], cancerMerged['pclat00']] if math.isnan(cancerMerged['pclat10']) else [cancerMerged['pclon10'], cancerMerged['pclat10']]
#query tree
for plantType in plantTypes:
    cancerMerged[plantType+'_tree'] = zip(subTrees[plantType].query(x=cancerMerged['coords'], k=50))

#look at points in vecotr magical way


pollutionRateDataframe = pd.DataFrame.from_dict(pollutionRateByCounty).transpose()
pollutionRateDataframe['fips'] = pollutionRateDataframe.index
fullData = cancerMerged.merge(pollutionRateDataframe, on="fips")
print(fullData)

subplotFigure = sp.make_subplots(rows=6, cols=1)
subplotFigure.add_trace(
    px.scatter_geo(fullData, lat='pclat10', lon='pclon10', size='Coal', hover_name='State'),
    row=1,
    col=1)
iterNumber = 1
for plantType in plantTypes:
    iterNumber += 1
    subplotFigure.add_trace(
        px.scatter(data_frame=fullData,
                   x=plantType,
                   y='ratePer100k',
                   trendline="ols",
                   color=px.Constant(plantType),
                   title=plantType,
                   ),
        row=iterNumber,
        col=1
    )
