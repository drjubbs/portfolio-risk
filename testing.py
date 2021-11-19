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
            finance.calc_npv(example1, discount=6), -25.6604))

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


if __name__ == '__main__':
    unittest.main()
