import pandas as pd
from scipy.spatial import cKDTree, distance
import plotly.express as px
import plotly.subplots as sp
import math
import numpy as np
from statsmodels import api as sm


#load in datasets
powerPlants = pd.read_csv(open('./dataFiles/global_power_plant_database.csv', encoding='utf-8'))
cancerRates = pd.read_csv(open('dataFiles/incd_lung.csv', encoding='utf-8'))
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
    cancerMerged[plantType+'Query'] = subTrees[plantType].query_ball_point(x=np.dstack([cancerMerged['coordLat'], cancerMerged['coordLon']]), r=10, workers=-1).transpose()

def sadnessFunction(plantType, queryPoints, long, lat):
    results = subPowerPlants[plantType].iloc[queryPoints]
    powerPlantLats = results['latitude'].values-lat
    powerPlantLons = results['longitude'].values - long
    powerPlantSizes = results['capacity_mw']
    score = np.sum(np.sqrt(np.sum([powerPlantLons**2, powerPlantLats**2])))
    return score

for plantType in plantTypes:
    cancerMerged[plantType+'Score'] = cancerMerged.apply(lambda row: sadnessFunction(plantType, row[plantType+'Query'], row['coordLon'], row['coordLat']), axis=1)
    print(plantType+" done")
#need to convert to subplots
cancerMerged['State'] = cancerMerged['State'].str.slice(stop=-3)
cancerMerged = cancerMerged.rename(columns={
            "WindScore": "Wind Proximity Value",
            "CoalScore": "Coal Proximity Value",
            "GasScore": "Gas Proximity Value",
            "HydroScore": "Hydroelectric Proximity Value",
            "OilScore": "Oil Proximity Value",
            "BiomassScore": "Biomass Proximity Value",
            "WasteScore": "Waste Proximity Value",
})
#px.scatter_geo(cancerMerged, lat='pclat10', lon='pclon10', size=["Wind Proximity Value", "Coal Proximity Value", "Gas Proximity Value", "Hydroelectric Proximity Value", "Oil Proximity Value", "Biomass Proximity Value", "Waste Proximity Value"], hover_name='State').show()

figure = px.scatter(data_frame=cancerMerged,
           hover_name='State',
           x=["Wind Proximity Value", "Coal Proximity Value", "Gas Proximity Value", "Hydroelectric Proximity Value", "Oil Proximity Value", "Biomass Proximity Value", "Waste Proximity Value"],
           y='ratePer100k',
           trendline="ols",
           title='Cancer Rates Per 100k residents versus their proximity to a power plant',
           labels={
               "x": "Proximity Value",
               "ratePer100k": "Cancer Rate Per 100,000 people, age adjusted"
           }
           )
figure.show()