#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Unit testing for financial functions"""
import datetime as dt
import unittest
import pandas as pd
import numpy as np
import finance


class TestFinance(unittest.TestCase):
    """Unit testing for financial functions"""

    def test_npv(self):
        """Unit testing for financial functions"""

        # Example 1 NPV
        dates = [dt.datetime(1981, 1, 1), dt.datetime(1982, 1, 1)]
        flows = [-120, 100]
        example1 = pd.DataFrame({
            'datetime': dates,
            'flows': flows,
        })

        self.assertTrue(np.isclose(
            finance.calc_npv(example1, discount=6), -25.6603773))

        # Example 2 NPV: Mix up date order
        dates = [dt.datetime(1983, 1, 1),
                 dt.datetime(1981, 1, 1),
                 dt.datetime(1985, 1, 1)
                 ]
        flows = [500, -1000, 800]
        example2 = pd.DataFrame({
            'datetime': dates,
            'flows': flows,
        })

        self.assertTrue(np.isclose(
            finance.calc_npv(example2, discount=8), 16.6932
        ))

        self.assertTrue(np.isclose(
            finance.calc_internal_ror(example2), 8.5683))

        # Example 3 NPV: Three investments
        dates = [dt.datetime(1979, 8, 1),
                 dt.datetime(1980, 8, 1),
                 dt.datetime(1981, 8, 1),
                 dt.datetime(1984, 8, 1)
                 ]
        flows = [-333.33, -333.33, -333.33, 1312.88]
        example3 = pd.DataFrame({
            'datetime': dates,
            'flows': flows,
        })

        self.assertAlmostEqual(finance.calc_internal_ror(example3),
                               7.0019386,
                               5)

    def test_finddates(self):
        """Tests for finding closest date in a DataFrame"""

        df_test = pd.read_csv("test_dates.csv", parse_dates=['datetime'])

        # March 1 should throw an exception because it is outside of the
        # DataFrame range.
        with self.assertRaises(ValueError):
            finance.return_closest_time(
                              df_test, dt.datetime(2021, 3, 1))

        # June 4th should be the first of month
        row = finance.return_closest_time(df_test, dt.datetime(2021, 6, 4))
        self.assertEqual(row.datetime.to_pydatetime(),
                         dt.datetime(2021, 6, 1))

        # June 24 splits two entries, we should get the first which is the 23
        row = finance.return_closest_time(df_test, dt.datetime(2021, 6, 24))
        self.assertEqual(row.datetime.to_pydatetime(),
                         dt.datetime(2021, 6, 23))

        # June 29th should give us the last entry
        row = finance.return_closest_time(df_test, dt.datetime(2021, 6, 29))
        self.assertEqual(row.datetime.to_pydatetime(),
                         dt.datetime(2021, 6, 30))

        # July 24 should throw an exception
        with self.assertRaises(ValueError):
            row = finance.return_closest_time(df_test, dt.datetime(2021, 7, 24))
            self.assertEqual(row.datetime.to_pydatetime(),
                             dt.datetime(2021, 6, 25))

    def test_create_flows(self):
        """Test routines which create cash flow DataFrames for NPV
        calculations."""

        # Create scratch DataFrame covering 30 years with a 7% ROR
        # This is a bit tricky we need to be careful with daily vs. yealy
        # compounding.
        dates = []
        adj_close = []
        x0 = 100        # Starting value for index
        rate = 0.07     # Rate of return
        for i in range(30):
            for j in range(12):
                dates.append(dt.datetime(1970+i, j+1, 1))
                num_years = (dates[-1]-dates[0]).days/365.25
                adj_close.append(x0*(1+rate)**num_years)

        df_test = pd.DataFrame({'datetime': dates, 'adj_close': adj_close})

        # Beginning of DataFrame frame, single investment, 10 years out
        df_flows1 = finance.create_flows(
                                    df_test,
                                    1000,
                                    dt.datetime(1970, 1, 1),
                                    [0],
                                    int(365.25*10))
        self.assertEqual(2, len(df_flows1))
        self.assertEqual(dt.datetime(1980, 1, 1),
                         df_flows1.iloc[-1, :].datetime.to_pydatetime())

        # IRR should be near 7...
        delta_rate = (7.0 - finance.calc_internal_ror(df_flows1))
        self.assertTrue(delta_rate < 0.01)

        # Offset in dataframe, investment split up...
        df_flows2 = finance.create_flows(
                                    df_test,
                                    1000,
                                    dt.datetime(1979, 7, 23),
                                    [0, 365, 2*365],
                                    int(365.25*5))

        delta_rate = (7.0 - finance.calc_internal_ror(df_flows2))
        self.assertTrue(delta_rate < 0.01)


if __name__ == '__main__':
    unittest.main()
