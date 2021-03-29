import pandas as pd
from scipy.spatial import cKDTree
import plotly.express as px
import numpy as np

# load in datasets
powerPlants = pd.read_csv(open('./dataFiles/global_power_plant_database.csv', encoding='utf-8'))
cancerRates = pd.read_csv(open('dataFiles/incd_lung.csv', encoding='utf-8'))
countyCenters = pd.read_csv(open('./dataFiles/county_centers.csv', encoding='utf-8'))

plantTypes = ['Nuclear', 'Wind', 'Solar', 'Coal', 'Gas', 'Hydro', 'Oil', 'Biomass', 'Waste']
plantRenewable = {
    'Nuclear': True,
    'Wind': True,
    'Solar': True,
    'Coal': False,
    'Gas': False,
    'Hydro': False,
    'Oil': False,
    'Biomass': False, #only kind of lol,for the purposes of pollution yes
    'Waste': True
}
# merge cancerRates and countyCenters datasets together
cancerMerged = cancerRates.merge(countyCenters, on="fips", how='left')
# setup dicts
subPowerPlants = {}
subTrees = {}
for plantType in plantTypes:
    subPowerPlants[plantType] = powerPlants.query("primary_fuel == '{}'".format(plantType))
    subTrees[plantType] = cKDTree(subPowerPlants[plantType][['latitude', 'longitude']].values)
# make coords
cancerMerged['coordLon'] = cancerMerged['pclon10'].combine_first(cancerMerged['pclon00'])
cancerMerged['coordLat'] = cancerMerged['pclat10'].combine_first(cancerMerged['pclat00'])
# query tree
for plantType in plantTypes:
    cancerMerged[plantType + 'Query'] = subTrees[plantType].query_ball_point(
        x=np.dstack([cancerMerged['coordLat'], cancerMerged['coordLon']]), r=10, workers=-1).transpose()


def sadnessFunction(plantType, queryPoints, long, lat):  # not as sad as it once was
    results = subPowerPlants[plantType].iloc[queryPoints]
    powerPlantLats = results['latitude'].values - lat
    powerPlantLons = results['longitude'].values - long
    powerPlantSizes = results['capacity_mw']
    score = np.sum(powerPlantSizes / np.sqrt(np.sum(np.array([powerPlantLons ** 2, powerPlantLats ** 2]).T, axis=1)))
    return score


for plantType in plantTypes:
    cancerMerged[plantType + 'Score'] = cancerMerged.apply(
        lambda row: sadnessFunction(plantType, row[plantType + 'Query'], row['coordLon'], row['coordLat']), axis=1)
    print(plantType + " done")

cancerMerged['State'] = cancerMerged['State'].str.slice(stop=-3)
newNameDict = {
    "WindScore": "Wind Proximity Value",
    "SolarScore": "Solar Proximity Value",
    "CoalScore": "Coal Proximity Value",
    "GasScore": "Gas Proximity Value",
    "HydroScore": "Hydroelectric Proximity Value",
    "OilScore": "Oil Proximity Value",
    "BiomassScore": "Biomass Proximity Value",
    "WasteScore": "Waste Proximity Value",
    "NuclearScore": "Nuclear Proximity Value"
}
cancerMerged = cancerMerged.rename(columns=newNameDict)
# px.scatter_geo(cancerMerged, lat='pclat10', lon='pclon10', size=["Wind Proximity Value", "Coal Proximity Value", "Gas Proximity Value", "Hydroelectric Proximity Value", "Oil Proximity Value", "Biomass Proximity Value", "Waste Proximity Value"], hover_name='State').show()

figure = px.scatter(data_frame=cancerMerged,
                    hover_name='State',
                    x=["Wind Proximity Value", "Solar Proximity Value", "Coal Proximity Value", "Gas Proximity Value",
                       "Hydroelectric Proximity Value", "Oil Proximity Value", "Biomass Proximity Value",
                       "Waste Proximity Value", "Nuclear Proximity Value"],
                    y='ratePer100k',
                    trendline="ols",
                    title='Cancer Rates Per 100k residents versus proximity to a power plant',
                    labels={
                        "x": "Proximity Value",
                        "ratePer100k": "Cancer Rate Per 100,000 people, age adjusted"
                    }
                    )
figure.update_layout(xaxis_title = "Proximity Score",
                     legend_title_text="Power Plant Type",
                     legend_traceorder='grouped',
                     legend_tracegroupgap=10)
#for trace in figure.data:
#   if plantRenewable[list(newNameDict.keys())[list(newNameDict.values()).index(trace.name)][:-5]]: #someone should take python away from me for this monstrosity
#       trace.legendgroup = 'Renewable'
#   else:
#       trace.legendgroup = 'Non-Renewable'
figure.show()
figure.write_html("scatter.html")
cancerMerged.to_csv('dataOutput/full.csv')
for item in ['fips', 'clon00', 'clat00', 'clon10', 'clat10', 'pclon00', 'pclat00', 'pclon10', 'pclat10',
                  'NuclearQuery', 'WindQuery', 'SolarQuery', 'CoalQuery', 'GasQuery', 'HydroQuery', 'OilQuery',
                  'BiomassQuery', 'WasteQuery']:
    cancerMerged.pop(item)
cancerMerged.to_csv('dataOutput/data.csv', index=False)
