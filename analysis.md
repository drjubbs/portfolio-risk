---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.13.1
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# S&P500 Pareto Analysis: Return and Risk versus Investment Schedule

The following notebook examines the trade-off between risk and return for investment into an index fund (in this case the Vanguard S&P500 tracking ETF/mutual fund. Specifically the analysis looks at one single lump sum investment versus three investments spread out equally in time.

As the investments are spread out, one expects the overall rate of return to go down. This is because investment money is sitting idle compared to the base case where everything is put into the market at once. Also as the investments are spread out, the risk envelope should shrink.

Two datasets are used for this analysis:

- `VFINX.csv`: Vanguard S&P500 Investor Shares adjusted close is used as a total return index (data from S&P Total Return is paywalled). 1980 to present
- `CPIAUCNS.csv`: Consumer Price Index for All Urban Consumers: All Items in U.S. City Average

```python
%load_ext autoreload
%autoreload 2
```

```html
<!-- Some CSS tweaks for mobile -->
<style>
div.output_subarea { max-width: 100%; }
</style>
```

```python
import pandas as pd
import numpy as np
from dateutil import parser
from datetime import datetime, timedelta
import plotly
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import finance
```

### Simulation Parameters

```python
# Time horizon to calculate ROR over in years
HORIZON = 10
```

# Part A: CPI Adjust Total Index Returns

```python
vfinx = pd.read_csv("VFINX.csv", parse_dates=['datetime']).dropna()
vfinx = vfinx.sort_values(by='datetime')
```

```python
vfinx
```

Let's do a basic plot of the index over time on a log scale.

```python
scatter_vfinx = go.Scatter(x=vfinx['datetime'], y=vfinx['adj_close'], name='VFINX')
fig = go.Figure()
fig.add_trace(scatter_vfinx)
fig.update_yaxes(type="log", title='Adjusted Close')
fig.update_xaxes(title='Year')
fig.update_layout(
     autosize=False,
     width=300,
     height=300,
     margin=dict(
         l=10, t=10, r=10, b=10))
fig.show()
```

CPI over time which is used to adjust index returns.

```python
cpi = pd.read_csv("CPIAUCNS.csv", parse_dates=['datetime'])
```

```python
scatter_cpi = go.Scatter(x=cpi['datetime'], y=cpi['CPIAUCNS'])
fig = go.Figure()
fig.add_trace(scatter_cpi)
fig.update_xaxes(title="Year")
fig.update_yaxes(title="CPI-AUCNS")
config={'displayModeBar': False}
fig.update_layout(
     autosize=False,
     width=300,
     height=300,
     margin=dict(
         l=10, t=10, r=10, b=10))
fig.show(config=config)
```

### Merge and adjust index for inflation

```python
# Create a column for months so we can merge with CPI data
months = vfinx['datetime'] 
vfinx['datetime_month']=[datetime(t.year,t.month, 1) for t in months]
```

```python
vfinx = vfinx.merge(cpi, how='left', left_on='datetime_month', right_on='datetime').dropna()
```

```python
# Clean up the DataFrame
vfinx = vfinx[['datetime_x', 'adj_close', 'CPIAUCNS']].copy()
vfinx = vfinx.rename(columns={'datetime_x': 'datetime', 'CPIAUCNS': 'cpi'})
vfinx
```

```python
# Make first row the start of the index adjustment
scaling = vfinx.iloc[0, :].cpi
vfinx['adj_close'] = vfinx['adj_close']*scaling/vfinx['cpi']
vfinx
```

### Compare non-adjusted and inflation adjusted index levels

```python
scatter_vfinx_cpi = go.Scatter(x=vfinx['datetime'], y=vfinx['adj_close'], name='VFINX CPI Adjusted')
fig = go.Figure()
fig.add_trace(scatter_vfinx)
fig.add_trace(scatter_vfinx_cpi)
fig.update_xaxes(title='Year')
fig.update_yaxes(type="log", title='Index Level')
fig.update_layout(
     autosize=False,
     width=300,
     height=300,
     margin=dict(
         l=10, t=10, r=10, b=10))
fig.update_layout(legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="left",
    x=0.01
))
fig.show()
```

# Part B: Rate of Return Over Time for a Lump Sum
Start with the simple case of putting money in as a lump sum. To generate "scenarios" / simulate, we will start with older historical data and walk forward in time, creating a new ROR each week (the VFINX data is weekly).

```python
df_ror0, go_histo0 = finance.rolling_rate_of_return(vfinx, [0], "Lump Sum", HORIZON)
```

Plot the ROR over time. Note the simulations stop in 2011 because we need 10 (or whatever `HORIZON` is set to) years of forward looking data.

```python
fig = go.Figure()
fig.add_trace(go.Scatter(x=df_ror0['datetime'], y=df_ror0['ror']))
fig.update_xaxes(title='Year of Initial Investment')
fig.update_yaxes(title='Simple Annualized ROR (%)')
fig.update_layout(
     autosize=False,
     width=300,
     height=300,
     margin=dict(
         l=10, t=10, r=10, b=10))
fig.show()
```

Histogram view of same data. Note this is not normally distributed, but we still will use standard deviation as a measure of the scatter in the data.

```python
fig = go.Figure()
fig.add_trace(go_histo0)
fig.update_layout(
     autosize=False,
     width=300,
     height=300,
     margin=dict(
         l=10, t=10, r=10, b=10))
fig.update_yaxes(title='Count')
fig.update_xaxes(title='Rate of Return (%)')
fig.show()
```

# Part C: Investment Divided into 3 Lumps, 1 Year Apart

```python
df_ror3, go_histo3 = finance.rolling_rate_of_return(vfinx, [0, 365.25, 2*365.25], "3 Parts, One Year Spacing", HORIZON)
```

Let's overlay the histograms, we should see some less extreme cases in the 3 lump strategy vs. single lump, but with the mean potentially lower.

```python
fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
fig.add_trace(go_histo0, row=1, col=1)
fig.add_trace(go_histo3, row=2, col=1)
fig.update_layout(barmode='overlay')
fig.update_layout(
     autosize=False,
     width=375,
     height=375,
     margin=dict(
         l=10, t=10, r=10, b=10))
fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1    
))
fig.update_yaxes(title='Count')
fig.update_xaxes(title='Rate of Return (%)')
fig.show()
```

Sanity check on results - the division into lumps should reduce overall return but also return the standard deviation of the returns. This is what will create the pareto curve.

```python
print(np.mean(df_ror0['ror']))
print(np.mean(df_ror3['ror']))
```

```python
print(np.std(df_ror0['ror']))
print(np.std(df_ror3['ror']))
```

Average rate of return for the index looks to be 7.4% which is inline with other estimates.


# Part D: Pareto Analysis

```python
offset_list = [[0]]
for i in range(24):
    offset_list.append([0, (i+1)*30, (i+1)*30*2])
```

```python
returns = []
stds = []
days = []
upper = []
lower = []

for offset, i in zip(offset_list, range(25)):
    print(offset)
    df_ror, _ = finance.rolling_rate_of_return(vfinx, offset, str(offset), HORIZON)
    
    days.append(i*30)
    returns.append(np.mean(df_ror['ror']))
    stds.append(np.std(df_ror['ror']))
    lower.append(np.percentile(df_ror['ror'], 2.5))
    upper.append(np.percentile(df_ror['ror'], 97.5))
```

### Basic Pareto Plot

What we would like to see here is an "efficient frontier" -- that is a knee in the curve where the tradeoff between risk and return looks optimal. Unfortunately we get more of a straight line which implies any de-risking will come at the expense of significant yield loss.

```python
pareto = go.Scatter(x=stds, y=returns, text=days)
fig = go.Figure()
fig.update_yaxes(title='Simple Return on S&P500 (%)')
fig.update_xaxes(title='Return St. Dev (%)')
fig.add_trace(pareto)
fig.update_layout(
     autosize=False,
     width=375,
     height=375,
     margin=dict(
         l=10, t=10, r=10, b=10))
fig.show()
```

### Risk Envelope Plot

A slightly different look at the same data, this time the error bars represent where 95% of the simulation experiments fell. Again, we fail to see the emergence of an "efficient frontier", indicating lump sum investment is probably the best strategy.

```python
trace_mean = go.Scatter(x=days, y=returns, name="Average")
trace_lower = go.Scatter(x=days, y=lower, name="Lower 5%")
trace_upper = go.Scatter(x=days, y=upper, name="Upper 95%")
fig=go.Figure()
fig.add_trace(trace_mean)
fig.add_trace(trace_upper)
fig.add_trace(trace_lower)
fig.update_xaxes(title='Spacing Between 3 Split Investments (Days)')
fig.update_yaxes(title='10 Year Rate of Return (%)')
fig.update_layout(
     autosize=False,
     width=375,
     height=375,
     margin=dict(
         l=10, t=10, r=10, b=10))
fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
))
fig.show()
```

```python

```
