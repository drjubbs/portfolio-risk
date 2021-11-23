#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Financial functions used to calculate net present value and internal rates of
return.
"""
import datetime as dt
from functools import partial
from scipy.optimize import root
import pandas as pd


def calc_npv(df_in, discount):
    """On input, Pandas DataFrame with `dates` and `flows` columns
    representing data and cash flow. Negative cash flows are investments,
    positive cash flows are divestments.

    `discount` is the yearly discount rate used, in percent.
    """

    df_in = df_in.sort_values(by='datetime')
    df_in.reset_index(inplace=True)
    df_in['time_delta'] = df_in['datetime'] - df_in.datetime[0]
    df_in['years_delta'] = [t.total_seconds() / (365.25 * 24 * 60 * 60) for t in
                            df_in['time_delta']]

    # Average out leap year effects
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
    """Calculate internal rate of return, similar to Excel IRR function.
    Note that this will return a ROR, compoundly yearly.
    """
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


def create_flows(df_dates, in_amount, dt_begin, in_offsets, out_offset):
    """Create a Pandas DataFrame for use in cash flow calculations.

    `df_dates`: DataFrame with a `datetime` column and `adj_close` column
                which contains a "database" of index values. For example, this
                might be a price level index for the S&P 500 index.
    `in_amount`: Amount of inital investment. Will be split into
                `len(in_spacing)` chunks.
    `in_begin`: Datetime object of when to start the initial investment.
    `in_offsets`: list of offsets, in days, over which the investment will
                  be spread out.
    `out_offset`: days corresponding to when divestment occurs.
    """

    # If invalid beginning time is given find the closest date
    dt_begin = return_closest_time(df_dates, dt_begin).datetime.to_pydatetime()

    # Create investment part of DataFrame
    in_rows = []
    for offset in in_offsets:
        in_rows.append(return_closest_time(
                            df_dates, dt_begin+dt.timedelta(days=offset)))
    df_in_flows = pd.DataFrame(in_rows)

    invest_amount = in_amount / len(in_offsets)
    df_in_flows['shares'] = invest_amount/df_in_flows['adj_close']
    df_in_flows['flows'] = -1.0*invest_amount
    shares = sum(df_in_flows.shares)

    # Divestment section
    dt_end = return_closest_time(df_dates, dt_begin+dt.timedelta(
        days=out_offset))
    dt_end['flows'] = shares*dt_end['adj_close']
    dt_end['shares'] = -shares
    df_out_flows = pd.DataFrame([dt_end])

    # Let's be paranoid and make sure columns line up
    df_in_flows = df_in_flows[['datetime', 'adj_close', 'shares', 'flows']]
    df_out_flows = df_out_flows[['datetime', 'adj_close', 'shares', 'flows']]

    return df_in_flows.append(df_out_flows)


def calc_simple_roi(df_in):
    """Calculate a simplified rate of return (investment in vs. out). Assumes
    `df_in` is sorted by date and returns ROI on a annualized basis
    """

    mask = df_in.flows < 0
    begin = df_in[mask].iloc[0, :].datetime.to_pydatetime()
    total_in = -1 * df_in[mask].flows.sum()

    mask = df_in.flows > 0
    end = df_in[df_in.flows > 0].iloc[-1, :].datetime.to_pydatetime()
    total_out = df_in[mask].flows.sum()

    years = (end-begin).days/365.25
    return (total_out-total_in)/total_in/years*100
