import pandas as pd
from scipy.spatial import cKDTree, distance
from sklearn.metrics.pairwise import paired_distances
import plotly.express as px
import plotly.subplots as sp
import math
import numpy as np



#load in datasets
powerPlants = pd.read_csv(open('./dataFiles/global_power_plant_database.csv', encoding='utf-8'))
cancerRates = pd.read_csv(open('dataFiles/incd_all.csv', encoding='utf-8'))
countyCenters = pd.read_csv(open('./dataFiles/county_centers.csv', encoding='utf-8'))

plantTypes = ['Wind', 'Coal', 'Gas', 'Hydro', 'Oil', 'Biomass', 'Waste']
#merge cancerRates and countyCenters datasets together
cancerMerged = cancerRates.merge(countyCenters, on="fips", how='left')
#setup dicts
subPowerPlants = {}
subTrees = {}
for plantType in plantTypes:
    subPowerPlants[plantType] = powerPlants.query("primary_fuel == '{}'".format(plantType))
    subTrees[plantType] = cKDTree(subPowerPlants[plantType][['latitude', 'longitude']].values)
#make coords
cancerMerged['coordLon'] = cancerMerged['pclon10'].combine_first(cancerMerged['pclon00'])
cancerMerged['coordLat'] = cancerMerged['pclat10'].combine_first(cancerMerged['pclat00'])
#query tree
for plantType in plantTypes:
    cancerMerged[plantType+'Query'] = subTrees[plantType].query_ball_point(x=np.dstack([cancerMerged['coordLat'], cancerMerged['coordLon']]), r=150, workers=-1).transpose()

def sadnessFunction(plantType, queryPoints, long, lat):
    results = subPowerPlants[plantType].iloc[queryPoints]
    try:
        score = sum(results['capacity_mw']/
                            distance.cdist(
                                [results['latitude'], results['longitude']],
                                np.repeat(np.asarray([np.asarray([lat, long])]), len(queryPoints), axis=0),
                            )

                    )
    except ValueError:
        print('error')
        return float("NAN")
    return score

for plantType in plantTypes:
    cancerMerged[plantType+'Score'] = cancerMerged.apply(lambda row: sadnessFunction(plantType, row[plantType+'Query'], row['coordLon'], row['coordLat']), axis=1)

#need to convert to subplots
#px.scatter_geo(cancerMerged, lat='pclat10', lon='pclon10', size='CoalScore', hover_name='State').show()
for plantType in plantTypes:
    px.scatter(data_frame=cancerMerged,
               x=plantType+'Score',
               y='ratePer100k',
               trendline="ols",
               color=px.Constant(plantType),
               title=plantType,
               ).show()
