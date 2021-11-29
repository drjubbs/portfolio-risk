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

- VFINX.csv: Vanguard S&P500 Investor Shares is used as a total return index (data from S&P Total Return is paywalled).
- CPIAUCNS.csv: Consumer Price Index for All Urban Consumers: All Items in U.S. City Average

```python
%load_ext autoreload
%autoreload 2
```

```python
import pandas as pd
import numpy as np
from dateutil import parser
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import finance
```

```python
# Time horizon to calculate ROR over in years
HORIZON = 10
```

```python
vfinx = pd.read_csv("VFINX.csv", parse_dates=['datetime']).dropna()
vfinx = vfinx.sort_values(by='datetime')
```

```python
vfinx
```

```python
scatter_vfinx = go.Scatter(x=vfinx['datetime'], y=vfinx['adj_close'], name='VFINX')
fig = go.Figure()
fig.add_trace(scatter_vfinx)
fig.update_yaxes(type="log")
fig.show()
```

```python
cpi = pd.read_csv("CPIAUCNS.csv", parse_dates=['datetime'])
```

```python
scatter_cpi = go.Scatter(x=cpi['datetime'], y=cpi['CPIAUCNS'])
fig = go.Figure()
fig.add_trace(scatter_cpi)
fig.show()
```

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

```python
scatter_vfinx_cpi = go.Scatter(x=vfinx['datetime'], y=vfinx['adj_close'], name='VFINX CPI Adjusted')
fig = go.Figure()
fig.add_trace(scatter_vfinx)
fig.add_trace(scatter_vfinx_cpi)
fig.update_xaxes(title='Year')
fig.update_yaxes(type="log", title='Index Level')
fig.show()
```

## Rate of return over time for a lump sum

```python
df_ror0, go_histo0 = finance.rolling_rate_of_return(vfinx, [0], "Lump Sum", HORIZON)
```

```python
fig = go.Figure()
fig.add_trace(go.Scatter(x=df_ror0['datetime'], y=df_ror0['ror']))
fig.update_xaxes(title='Year of Initial Investment')
fig.update_yaxes(title='Simple Annualized ROR (%)')
fig.show()
```

```python
fig = go.Figure()
fig.add_trace(go_histo0)
fig.show()
```

# Divided into 3 lumps, 1 year apart

```python
df_ror3, go_histo3 = finance.rolling_rate_of_return(vfinx, [0, 365.25, 2*365.25], "3 Lumps, One Year Spacing", HORIZON)
```

```python
fig = go.Figure()
fig.add_trace(go_histo0)
fig.add_trace(go_histo3)
fig.update_layout(barmode='overlay')
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

```python

```
