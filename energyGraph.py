import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

powerPlants = pd.read_csv(open('dataFiles/global_power_plant_database.csv', encoding='utf-8'))
powerSum = powerPlants.groupby('primary_fuel').sum()
countSum = powerPlants['primary_fuel'].value_counts()
figure = make_subplots(rows=1,
                       cols=2,
                       subplot_titles=("Breakdown of power plants by generation capacity",
                                        "Breakdown of power plants by quantity"))
figure.add_trace(go.Pie(values=powerSum['capacity_mw'], labels=powerSum.index, domain=dict(x=[0, 0.5])))
figure.add_trace(go.Pie(values=countSum.values, labels=countSum.index, domain=dict(x=[0.5, 1])))
figure.show()