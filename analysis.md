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
vfinx['cpi_adj_close'] = vfinx['adj_close']*scaling/vfinx['cpi']
vfinx
```

```python
scatter_vfinx_cpi = go.Scatter(x=vfinx['datetime'], y=vfinx['cpi_adj_close'], name='VFINX CPI Adjusted')
fig = go.Figure()
fig.add_trace(scatter_vfinx)
fig.add_trace(scatter_vfinx_cpi)
fig.update_xaxes(title='Year')
fig.update_yaxes(type="log", title='Index Level')
fig.show()
```

## Rate of return, lump sum

```python
# Start at the first date we have index data for
start = vfinx.iloc[0,:].datetime.to_pydatetime()
end = vfinx.iloc[-1,:].datetime.to_pydatetime()-timedelta(365*HORIZON)
print("{0} to {1}".format(start, end))
```

```python
this_start = start
desired_end = start + timedelta(365*HORIZON)
```

```python
invest = -100*vfinx[vfinx.datetime==this_start].cpi_adj_close[0]
```

```python
row = finance.return_closest_time(vfinx, desired_end)
divest = 100*row.cpi_adj_close
this_end = row.datetime
print("Requested end: {0} Actual end: {1}".format(desired_end, this_end))
```

```python
df_irr = pd.DataFrame({'datetime': [this_start, this_end], 'flows': [invest, divest]})
df_irr
```

```python
finance.calc_npv(df_irr, -200)
```

Calculate the NPV at several rates of return over an internval. Where this function crosses zero is the internal rate of return.

```python
npv = []
rates = np.linspace(0,15)
for rate in rates:    
    npv.append(finance.calc_npv(df_irr, rate))
npv = go.Scatter(x=rates, y=npv, name='npv')
fig = go.Figure()
fig.add_trace(npv)
fig.update_xaxes(title='Discount Rate %)')
fig.update_yaxes(title='NPV')
fig.show()
```

```python
finance.calc_internal_ror(df_irr)
```

```python

```
