import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express.colors as px


eval_file = 'evaluate_results.csv'
eval_file = os.path.join('archive_ignore/outputs', eval_file)
data_eval = pd.read_csv(eval_file)

forecast_file = 'forecast_results.csv'
forecast_file = os.path.join('archive_ignore/outputs', forecast_file)
data_forecast = pd.read_csv(forecast_file)

cmap = px.qualitative.Plotly

# eval scatter ---------------------------------------------------------------------------------------------------------
model_names = data_eval['Model'].values
traces_eval = []
colors = [cmap[i % len(cmap)] for i in range(len(model_names))]
for i, model_name in enumerate(model_names):
    trace = go.Scatter(
        x=data_eval.columns[1:],
        y=data_eval[data_eval['Model'] == model_name].values.tolist()[0][1:],
        name=model_name,
        mode='markers',
        hovertext=[model_name] * len(data_eval.columns[1:]),
        hoverinfo='text',
        marker=dict(
            size=10,
            opacity=0.8,
            color=colors[i]
        )
    )
    traces_eval.append(trace)

fig_scatter_eval = go.Figure(data=traces_eval)


# forecast scatter -----------------------------------------------------------------------------------------------------
model_names = data_forecast['Model'].values
traces_forecast = []
colors = [cmap[i % len(cmap)] for i in range(len(model_names))]
for i, model_name in enumerate(model_names):
    trace = go.Scatter(
        x=data_forecast.columns[1:],
        y=data_forecast[data_forecast['Model'] == model_name].values.tolist()[0][1:],
        name=model_name,
        mode='markers',
        hovertext=[model_name] * len(data_forecast.columns[1:]),
        hoverinfo='text',
        marker=dict(
            size=10,
            opacity=0.8,
            color=colors[i]
        )
    )
    traces_forecast.append(trace)

fig_scatter_forecast = go.Figure(data=traces_forecast)


# forecast table -------------------------------------------------------------------------------------------------------
forecast_average_ranks = []
for column in data_forecast.columns[1:]:
    data_forecast[column] = data_forecast[column].rank(method='min').astype(int)
    forecast_average_ranks.append(data_forecast[column].values)
    best = data_forecast.nsmallest(3, column)[column].index
    data_forecast.loc[best[0], column] = str(data_forecast.loc[best[0], column]) + ' 🥇'
    data_forecast.loc[best[1], column] = str(data_forecast.loc[best[1], column]) + ' 🥈'
    data_forecast.loc[best[2], column] = str(data_forecast.loc[best[2], column]) + ' 🥉'
forecast_average_ranks = np.array(forecast_average_ranks).mean(axis=0)

trace_table_forecast = go.Table(
    header=dict(values=list(data_forecast.columns)),
    cells=dict(values=[data_forecast[col] for col in data_forecast.columns])
)
fig_table_forecast = go.Figure(data=[trace_table_forecast])


# eval table -------------------------------------------------------------------------------------------------------
for column in data_eval.columns[1:]:
    data_eval[column] = data_eval[column].rank(method='min').astype(int)
    # best = data_eval.nsmallest(1, column)[column].index
    # data_eval.loc[best, column] = data_eval.loc[best, column].astype(str) + ' 🥇'
    best = data_eval.nsmallest(3, column)[column].index
    data_eval.loc[best[0], column] = str(data_eval.loc[best[0], column]) + ' 🥇'
    data_eval.loc[best[1], column] = str(data_eval.loc[best[1], column]) + ' 🥈'
    data_eval.loc[best[2], column] = str(data_eval.loc[best[2], column]) + ' 🥉'
    if column == 'Overall':
        best_eval = best[0]
trace_table_eval = go.Table(
    header=dict(values=list(data_eval.columns)),
    cells=dict(values=[data_eval[col] for col in data_eval.columns])
)
fig_table_eval = go.Figure(data=[trace_table_eval])


# Add Traces to Figure -------------------------------------------------------------------------------------------------
fig = make_subplots(rows=4, cols=1, specs=[[{'type': 'table'}], [{'type': 'table'}],
                                           [{'type': 'scatter'}], [{'type': 'scatter'}]],
                    vertical_spacing=0.05,
                    horizontal_spacing=0,
                    row_heights=[0.2, 0.2, 0.3, 0.3],
                    subplot_titles=("Evaluate Table", "Forecast Table", "Evaluate Scatter", "Forecast Scatter"),
                    )
fig.update_layout(
    title='Leaderboard',
    legend=dict(
        title='Models',
        orientation="h",
        yanchor="bottom",
        y=-0.2,
        xanchor="left",
        x=0
    ),
    height=1600
)

fig.add_trace(trace_table_eval, row=1, col=1)
fig.add_trace(trace_table_forecast, row=2, col=1)
for trace in traces_eval:
    fig.add_trace(trace, row=3, col=1)
for trace in traces_forecast:
    fig.add_trace(trace, row=4, col=1)

fig.update_xaxes(title_text="Dataset", row=3, col=1)
fig.update_xaxes(title_text="Dataset", row=4, col=1)
fig.update_yaxes(title_text="Costs", row=3, col=1)
fig.update_yaxes(title_text="Globally Normalised Mean Absolute Error", row=4, col=1)
fig.show()


# leaderboard.md -------------------------------------------------------------------------------------------------------
best_forecast = np.argmin(forecast_average_ranks)
data_forecast['Overall'] = forecast_average_ranks
data_forecast['Overall'] = data_forecast['Overall'].rank(method='min').astype(int)

last_col = data_forecast.columns[-1]
first_col = data_forecast.columns[0]
other_cols = data_forecast.columns[1:-1]
new_cols = [first_col] + [last_col] + list(other_cols)
data_forecast = data_forecast[new_cols]

best = data_forecast.nsmallest(3, 'Overall')['Overall'].index
data_forecast.loc[best[0], 'Overall'] = str(data_forecast.loc[best[0], 'Overall']) + ' 🥇'
data_forecast.loc[best[1], 'Overall'] = str(data_forecast.loc[best[1], 'Overall']) + ' 🥈'
data_forecast.loc[best[2], 'Overall'] = str(data_forecast.loc[best[2], 'Overall']) + ' 🥉'

with open('archive_ignore/outputs/leaderboard.md', 'w', encoding='utf-8') as f:
    f.write('# Leaderboard\n')

    f.write('### Evaluation \n')
    f.write(f'Best Model = {data_eval.iloc[best_eval]["Model"]}\n')
    f.write('\n')
    f.write(data_eval.to_html(index=False))
    f.write('\n')
    f.write('\n')

    f.write('### Forecast \n')
    f.write(f'Best Model = {data_forecast.iloc[best_forecast]["Model"]}\n')
    f.write('\n')
    f.write(data_forecast.to_html(index=False))
    f.write('\n')
    f.write('\n')
