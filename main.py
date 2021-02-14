import pandas as pd
from scipy.spatial import KDTree
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import math

app = dash.Dash(__name__)
#test for a commit

powerPlants = pd.read_csv(open('./dataFiles/global_power_plant_database.csv', encoding='utf-8'))
cancerRates = pd.read_csv(open('dataFiles/incd_all.csv', encoding='utf-8'))
countyCenters = pd.read_csv(open('./dataFiles/county_centers.csv', encoding='utf-8'))


cancerMerged = cancerRates.merge(countyCenters, on="fips", how='right')
powerPlants = powerPlants.query("primary_fuel == 'Coal'")
tree = KDTree(powerPlants[['latitude', 'longitude']].values)

figure = go.Figure()
pollutionRateByCounty = [0] * len(cancerMerged)
print(cancerMerged)
for county in cancerMerged.iterrows():
    if math.isnan(county[1]['pclon10']):
        coords = [county[1]['pclon00'], county[1]['pclat00']]
    else:
        coords = [county[1]['pclon10'], county[1]['pclat10']]
    treeResults = tree.query(x=coords, k=150)
    for treeResult in zip(treeResults[0], treeResults[1]):
        if math.isinf(treeResult[0]):
            continue
        try:
            result = powerPlants.iloc[treeResult[1]]
        except IndexError:
            print([county[1]['pclon10'], county[1]['pclat10']])
            print(county)
        pollutionRateByCounty[county[0]] += result['capacity_mw'] / math.pow(treeResult[0], 2)

cancerMerged.insert(6, 'pollutionScore', pollutionRateByCounty)

chart1 = px.scatter(data_frame=cancerMerged, x='pollutionScore', y='ratePer100k', trendline="ols", hover_name='State')
chart2 = px.scatter_geo(cancerMerged, lat='pclat10', lon='pclon10', size='pollutionScore', hover_name='State')
chart1.show()
chart2.show()
