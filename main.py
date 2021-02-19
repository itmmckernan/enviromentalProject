import pandas as pd
from scipy.spatial import cKDTree
import plotly.express as px
import plotly.subplots as sp
import math
import numpy as np


powerPlants = pd.read_csv(open('./dataFiles/global_power_plant_database.csv', encoding='utf-8'))
cancerRates = pd.read_csv(open('dataFiles/incd_all.csv', encoding='utf-8'))
countyCenters = pd.read_csv(open('./dataFiles/county_centers.csv', encoding='utf-8'))

plantTypes = ['Wind', 'Coal', 'Gas', 'Hydro', 'Oil', 'Biomass', 'Waste']
cancerMerged = cancerRates.merge(countyCenters, on="fips", how='left')
pollutionRateByCounty = {}
subPowerPlants = {}
subTrees = {}
for plantType in plantTypes:
    subPowerPlants[plantType] = powerPlants.query("primary_fuel == '{}'".format(plantType))
    subTrees[plantType] = cKDTree(subPowerPlants[plantType][['latitude', 'longitude']].values)
"""
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
"""
#make coords
cancerMerged['coordLon'] = cancerMerged['pclon10'].combine_first(cancerMerged['pclon00'])
cancerMerged['coordLat'] = cancerMerged['pclat10'].combine_first(cancerMerged['pclat00'])


#query tree
for plantType in plantTypes:
    cancerMerged[plantType+'Query'] = subTrees[plantType].query_ball_point(x=np.dstack([cancerMerged['pclon10'], cancerMerged['coordLat']]), r=100, workers=-1).transpose()
#look at points in vecotr magical way

for plantType in plantTypes:
    cancerMerged[plantType+'Score'] = sum(subPowerPlants[plantType].values[cancerMerged[plantType+'Query']] / np.square(cancerMerged[plantType+'Query']))
    #in order for this to work it needs 2 layers of vectorization and neither numpy nor my brain is having it

#code below is depricated, need to get above code working to know what to change
pollutionRateDataframe = pd.DataFrame.from_dict(pollutionRateByCounty).transpose()
pollutionRateDataframe['fips'] = pollutionRateDataframe.index
fullData = cancerMerged.merge(pollutionRateDataframe, on="fips")
print(fullData)


px.scatter_geo(fullData, lat='pclat10', lon='pclon10', size='Coal', hover_name='State').show()
for plantType in plantTypes:
    px.scatter(data_frame=fullData,
               x=plantType+'Score',
               y='ratePer100k',
               trendline="ols",
               color=px.Constant(plantType),
               title=plantType,
               ).show()
