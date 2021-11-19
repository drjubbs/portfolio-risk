#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Financial functions used to calculate net present value and internal rates of
return.
"""
from functools import partial
from scipy.optimize import root


def calc_npv(df_in, discount):
    """On input, Pandas DataFrame with `dates` and `flows` columns
    representing data and cash flow. Negative cash flows are investments,
    positive cash flows are divestments.

    `discount` is the discount rate used in percent
    """

    df_in = df_in.sort_values(by='datetime')
    df_in.reset_index(inplace=True)
    df_in['time_delta'] = df_in['datetime'] - df_in.datetime[0]
    df_in['years_delta'] = [t.total_seconds() / (365 * 24 * 60 * 60) for t in
                            df_in['time_delta']]

    # Average out leap year effects, found
    df_in['years_delta'] = [round(t, 2) for t in df_in['years_delta']]

    # Calculate net present value at oldest date
    discount_flows = []
    for _, row in df_in.iterrows():
        if (1 + discount/100) == 0:
            npv = row['flows']
        else:
            npv = row['flows'] / ((1 + discount / 100) ** (row['years_delta']))
        discount_flows.append(npv)

    return sum(discount_flows)


def calc_internal_ror(df_in):
    """Calculate internal rate of return, similar to Excel IRR function"""
    df_in = df_in.sort_values(by='datetime')
    f_partial = partial(calc_npv, df_in)
    soln = root(f_partial, x0=6, method='lm')

    return soln.x[0]


def return_closest_time(df_in, date_in):
    """Given a DataFrame with a `datetime` column, find the row which is
    closests to `date_in` and return as a series.

    If two dates are equi-distant, take the earlier date. Throw an exception
    if the requested date is outside of the timespan of the data frame.
    """

    df_in = df_in.sort_values(by='datetime')

    if date_in < df_in.datetime.min().to_pydatetime():
        raise ValueError("date_in prior to begin of DataFrame")

    if date_in > df_in.datetime.max().to_pydatetime():
        raise ValueError("date_in after end of DataFrame")

    time_deltas = abs(df_in.datetime-date_in)
    mask = time_deltas == min(time_deltas)
    return df_in[mask].iloc[0, :]
