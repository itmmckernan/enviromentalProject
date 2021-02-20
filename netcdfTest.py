import pandas as pd
import plotly.express as px
from plotly.graph_objs import *
powerPlants = pd.read_csv(open('./dataFiles/global_power_plant_database.csv', encoding='utf-8'))

queryResults = powerPlants.query("commissioning_year == 2018")
countDict = {}
for item in queryResults.iterrows():
    try:
        countDict[item[1]['primary_fuel']] += item[1]['capacity_mw']
    except:
        countDict[item[1]['primary_fuel']] = item[1]['capacity_mw']


layout = Layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    title_x=0.5,
    font=dict(
        family="Courier New, monospace",
        size=50,
        color="Black"
    )
)

print(countDict)
keys, values = zip(*countDict.items())
figure = px.pie(names=keys, values=values, title="New Power Generation That Came Online in 2018")
figure.update_layout(layout)
figure.show()
