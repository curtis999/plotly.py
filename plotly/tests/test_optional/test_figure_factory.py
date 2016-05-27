from unittest import TestCase
from plotly.graph_objs import graph_objs as go
from plotly.exceptions import PlotlyError

import plotly.tools as tls
from plotly.tests.test_optional.optional_utils import NumpyTestUtilsMixin
import math
from nose.tools import raises

import numpy as np
from scipy.spatial import Delaunay
import pandas as pd


class TestDistplot(TestCase):

    def test_wrong_curve_type(self):

        # check: PlotlyError (and specific message) is raised if curve_type is
        # not 'kde' or 'normal'

        kwargs = {'hist_data': [[1, 2, 3]], 'group_labels': ['group'],
                  'curve_type': 'curve'}
        self.assertRaisesRegexp(PlotlyError, "curve_type must be defined as "
                                             "'kde' or 'normal'",
                                tls.FigureFactory.create_distplot, **kwargs)

    def test_wrong_histdata_format(self):

        # check: PlotlyError if hist_data is not a list of lists or list of
        # np.ndarrays (if hist_data is entered as just a list the function
        # will fail)

        kwargs = {'hist_data': [1, 2, 3], 'group_labels': ['group']}
        self.assertRaises(PlotlyError, tls.FigureFactory.create_distplot,
                          **kwargs)

    def test_unequal_data_label_length(self):
        kwargs = {'hist_data': [[1, 2]], 'group_labels': ['group', 'group2']}
        self.assertRaises(PlotlyError, tls.FigureFactory.create_distplot,
                          **kwargs)

        kwargs = {'hist_data': [[1, 2], [1, 2, 3]], 'group_labels': ['group']}
        self.assertRaises(PlotlyError, tls.FigureFactory.create_distplot,
                          **kwargs)

    def test_simple_distplot_prob_density(self):

        # we should be able to create a single distplot with a simple dataset
        # and default kwargs

        dp = tls.FigureFactory.create_distplot(hist_data=[[1, 2, 2, 3]],
                                               group_labels=['distplot'],
                                               histnorm='probability density')
        expected_dp_layout = {'barmode': 'overlay',
                              'hovermode': 'closest',
                              'legend': {'traceorder': 'reversed'},
                              'xaxis1': {'anchor': 'y2', 'domain': [0.0, 1.0], 'zeroline': False},
                              'yaxis1': {'anchor': 'free', 'domain': [0.35, 1], 'position': 0.0},
                              'yaxis2': {'anchor': 'x1',
                                         'domain': [0, 0.25],
                                         'dtick': 1,
                                         'showticklabels': False}}
        self.assertEqual(dp['layout'], expected_dp_layout)

        expected_dp_data_hist = {'autobinx': False,
                                 'histnorm': 'probability density',
                                 'legendgroup': 'distplot',
                                 'marker': {'color': 'rgb(31, 119, 180)'},
                                 'name': 'distplot',
                                 'opacity': 0.7,
                                 'type': 'histogram',
                                 'x': [1, 2, 2, 3],
                                 'xaxis': 'x1',
                                 'xbins': {'end': 3.0, 'size': 1.0, 'start': 1.0},
                                 'yaxis': 'y1'}
        self.assertEqual(dp['data'][0], expected_dp_data_hist)

        expected_dp_data_rug = {'legendgroup': 'distplot',
                                'marker': {'color': 'rgb(31, 119, 180)',
                                           'symbol': 'line-ns-open'},
                                'mode': 'markers',
                                'name': 'distplot',
                                'showlegend': False,
                                'text': None,
                                'type': 'scatter',
                                'x': [1, 2, 2, 3],
                                'xaxis': 'x1',
                                'y': ['distplot', 'distplot',
                                      'distplot', 'distplot'],
                                'yaxis': 'y2'}
        self.assertEqual(dp['data'][2], expected_dp_data_rug)

    def test_simple_distplot_prob(self):

        # we should be able to create a single distplot with a simple dataset
        # and default kwargs

        dp = tls.FigureFactory.create_distplot(hist_data=[[1, 2, 2, 3]],
                                               group_labels=['distplot'], histnorm='probability')
        expected_dp_layout = {'barmode': 'overlay',
                              'hovermode': 'closest',
                              'legend': {'traceorder': 'reversed'},
                              'xaxis1': {'anchor': 'y2', 'domain': [0.0, 1.0], 'zeroline': False},
                              'yaxis1': {'anchor': 'free', 'domain': [0.35, 1], 'position': 0.0},
                              'yaxis2': {'anchor': 'x1',
                                         'domain': [0, 0.25],
                                         'dtick': 1,
                                         'showticklabels': False}}
        self.assertEqual(dp['layout'], expected_dp_layout)

        expected_dp_data_hist = {'autobinx': False,
                                 'histnorm': 'probability',
                                 'legendgroup': 'distplot',
                                 'marker': {'color': 'rgb(31, 119, 180)'},
                                 'name': 'distplot',
                                 'opacity': 0.7,
                                 'type': 'histogram',
                                 'x': [1, 2, 2, 3],
                                 'xaxis': 'x1',
                                 'xbins': {'end': 3.0, 'size': 1.0, 'start': 1.0},
                                 'yaxis': 'y1'}
        self.assertEqual(dp['data'][0], expected_dp_data_hist)

        expected_dp_data_rug = {'legendgroup': 'distplot',
                                'marker': {'color': 'rgb(31, 119, 180)',
                                           'symbol': 'line-ns-open'},
                                'mode': 'markers',
                                'name': 'distplot',
                                'showlegend': False,
                                'text': None,
                                'type': 'scatter',
                                'x': [1, 2, 2, 3],
                                'xaxis': 'x1',
                                'y': ['distplot', 'distplot',
                                      'distplot', 'distplot'],
                                'yaxis': 'y2'}
        self.assertEqual(dp['data'][2], expected_dp_data_rug)

    def test_distplot_more_args_prob_dens(self):

        # we should be able to create a distplot with 2 datasets no
        # rugplot, defined bin_size, and added title

        hist1_x = [0.8, 1.2, 0.2, 0.6, 1.6,
                   -0.9, -0.07, 1.95, 0.9, -0.2,
                   -0.5, 0.3, 0.4, -0.37, 0.6]
        hist2_x = [0.8, 1.5, 1.5, 0.6, 0.59,
                   1.0, 0.8, 1.7, 0.5, 0.8,
                   -0.3, 1.2, 0.56, 0.3, 2.2]

        hist_data = [hist1_x] + [hist2_x]
        group_labels = ['2012', '2013']

        dp = tls.FigureFactory.create_distplot(hist_data, group_labels,
                                               histnorm='probability density',
                                               show_rug=False, bin_size=.2)
        dp['layout'].update(title='Dist Plot')

        expected_dp_layout = {'barmode': 'overlay',
                              'hovermode': 'closest',
                              'legend': {'traceorder': 'reversed'},
                              'title': 'Dist Plot',
                              'xaxis1': {'anchor': 'y2', 'domain': [0.0, 1.0],
                                         'zeroline': False},
                              'yaxis1': {'anchor': 'free', 'domain': [0.0, 1],
                                         'position': 0.0}}
        self.assertEqual(dp['layout'], expected_dp_layout)

        expected_dp_data_hist_1 = {'autobinx': False,
                                   'histnorm': 'probability density',
                                   'legendgroup': '2012',
                                   'marker': {'color': 'rgb(31, 119, 180)'},
                                   'name': '2012',
                                   'opacity': 0.7,
                                   'type': 'histogram',
                                   'x': [0.8, 1.2, 0.2, 0.6, 1.6, -0.9, -0.07,
                                         1.95, 0.9, -0.2, -0.5, 0.3, 0.4,
                                         -0.37, 0.6],
                                   'xaxis': 'x1',
                                   'xbins': {'end': 1.95, 'size': 0.2,
                                             'start': -0.9},
                                   'yaxis': 'y1'}
        self.assertEqual(dp['data'][0], expected_dp_data_hist_1)

        expected_dp_data_hist_2 = {'autobinx': False,
                                   'histnorm': 'probability density',
                                   'legendgroup': '2013',
                                   'marker': {'color': 'rgb(255, 127, 14)'},
                                   'name': '2013',
                                   'opacity': 0.7,
                                   'type': 'histogram',
                                   'x': [0.8, 1.5, 1.5, 0.6, 0.59, 1.0, 0.8,
                                         1.7, 0.5, 0.8, -0.3, 1.2, 0.56, 0.3,
                                         2.2],
                                   'xaxis': 'x1',
                                   'xbins': {'end': 2.2, 'size': 0.2,
                                             'start': -0.3},
                                   'yaxis': 'y1'}
        self.assertEqual(dp['data'][1], expected_dp_data_hist_2)

    def test_distplot_more_args_prob(self):

        # we should be able to create a distplot with 2 datasets no
        # rugplot, defined bin_size, and added title

        hist1_x = [0.8, 1.2, 0.2, 0.6, 1.6,
                   -0.9, -0.07, 1.95, 0.9, -0.2,
                   -0.5, 0.3, 0.4, -0.37, 0.6]
        hist2_x = [0.8, 1.5, 1.5, 0.6, 0.59,
                   1.0, 0.8, 1.7, 0.5, 0.8,
                   -0.3, 1.2, 0.56, 0.3, 2.2]

        hist_data = [hist1_x] + [hist2_x]
        group_labels = ['2012', '2013']

        dp = tls.FigureFactory.create_distplot(hist_data, group_labels,
                                               histnorm='probability',
                                               show_rug=False, bin_size=.2)
        dp['layout'].update(title='Dist Plot')

        expected_dp_layout = {'barmode': 'overlay',
                              'hovermode': 'closest',
                              'legend': {'traceorder': 'reversed'},
                              'title': 'Dist Plot',
                              'xaxis1': {'anchor': 'y2', 'domain': [0.0, 1.0],
                                         'zeroline': False},
                              'yaxis1': {'anchor': 'free', 'domain': [0.0, 1],
                                         'position': 0.0}}
        self.assertEqual(dp['layout'], expected_dp_layout)

        expected_dp_data_hist_1 = {'autobinx': False,
                                   'histnorm': 'probability',
                                   'legendgroup': '2012',
                                   'marker': {'color': 'rgb(31, 119, 180)'},
                                   'name': '2012',
                                   'opacity': 0.7,
                                   'type': 'histogram',
                                   'x': [0.8, 1.2, 0.2, 0.6, 1.6, -0.9, -0.07,
                                         1.95, 0.9, -0.2, -0.5, 0.3, 0.4,
                                         -0.37, 0.6],
                                   'xaxis': 'x1',
                                   'xbins': {'end': 1.95, 'size': 0.2,
                                             'start': -0.9},
                                   'yaxis': 'y1'}
        self.assertEqual(dp['data'][0], expected_dp_data_hist_1)

        expected_dp_data_hist_2 = {'autobinx': False,
                                   'histnorm': 'probability',
                                   'legendgroup': '2013',
                                   'marker': {'color': 'rgb(255, 127, 14)'},
                                   'name': '2013',
                                   'opacity': 0.7,
                                   'type': 'histogram',
                                   'x': [0.8, 1.5, 1.5, 0.6, 0.59, 1.0, 0.8,
                                         1.7, 0.5, 0.8, -0.3, 1.2, 0.56, 0.3,
                                         2.2],
                                   'xaxis': 'x1',
                                   'xbins': {'end': 2.2, 'size': 0.2,
                                             'start': -0.3},
                                   'yaxis': 'y1'}
        self.assertEqual(dp['data'][1], expected_dp_data_hist_2)

        def test_distplot_binsize_array_prob(self):
            hist1_x = [0.8, 1.2, 0.2, 0.6, 1.6, -0.9, -0.07, 1.95, 0.9, -0.2,
                       -0.5, 0.3, 0.4, -0.37, 0.6]
            hist2_x = [0.8, 1.5, 1.5, 0.6, 0.59, 1.0, 0.8, 1.7, 0.5, 0.8, -0.3,
                       1.2, 0.56, 0.3, 2.2]

            hist_data = [hist1_x, hist2_x]
            group_labels = ['2012', '2013']

            dp = tls.FigureFactory.create_distplot(hist_data, group_labels,
                                                   histnorm='probability',
                                                   show_rug=False,
                                                   bin_size=[.2, .2])

            expected_dp_data_hist_1 = {'autobinx': False,
                                       'histnorm': 'probability density',
                                       'legendgroup': '2012',
                                       'marker':
                                       {'color': 'rgb(31, 119, 180)'},
                                       'name': '2012',
                                       'opacity': 0.7,
                                       'type': 'histogram',
                                       'x': [0.8, 1.2, 0.2, 0.6, 1.6, -0.9,
                                             -0.07, 1.95, 0.9, -0.2, -0.5, 0.3,
                                             0.4, -0.37, 0.6],
                                       'xaxis': 'x1',
                                       'xbins': {'end': 1.95, 'size': 0.2,
                                                 'start': -0.9},
                                       'yaxis': 'y1'}
            self.assertEqual(dp['data'][0], expected_dp_data_hist_1)

            expected_dp_data_hist_2 = {'autobinx': False,
                                       'histnorm': 'probability density',
                                       'legendgroup': '2013',
                                       'marker':
                                       {'color': 'rgb(255, 127, 14)'},
                                       'name': '2013',
                                       'opacity': 0.7,
                                       'type': 'histogram',
                                       'x': [0.8, 1.5, 1.5, 0.6, 0.59, 1.0,
                                             0.8, 1.7, 0.5, 0.8, -0.3, 1.2,
                                             0.56, 0.3, 2.2],
                                       'xaxis': 'x1',
                                       'xbins': {'end': 2.2, 'size': 0.2,
                                                 'start': -0.3},
                                       'yaxis': 'y1'}
            self.assertEqual(dp['data'][1], expected_dp_data_hist_2)

        def test_distplot_binsize_array_prob_density(self):
            hist1_x = [0.8, 1.2, 0.2, 0.6, 1.6, -0.9, -0.07, 1.95, 0.9, -0.2,
                       -0.5, 0.3, 0.4, -0.37, 0.6]
            hist2_x = [0.8, 1.5, 1.5, 0.6, 0.59, 1.0, 0.8, 1.7, 0.5, 0.8, -0.3,
                       1.2, 0.56, 0.3, 2.2]

            hist_data = [hist1_x, hist2_x]
            group_labels = ['2012', '2013']

            dp = tls.FigureFactory.create_distplot(hist_data, group_labels,
                                                   histnorm='probability',
                                                   show_rug=False,
                                                   bin_size=[.2, .2])

            expected_dp_data_hist_1 = {'autobinx': False,
                                       'histnorm': 'probability density',
                                       'legendgroup': '2012',
                                       'marker':
                                       {'color': 'rgb(31, 119, 180)'},
                                       'name': '2012',
                                       'opacity': 0.7,
                                       'type': 'histogram',
                                       'x': [0.8, 1.2, 0.2, 0.6, 1.6, -0.9,
                                             -0.07, 1.95, 0.9, -0.2, -0.5, 0.3,
                                             0.4, -0.37, 0.6],
                                       'xaxis': 'x1',
                                       'xbins': {'end': 1.95, 'size': 0.2,
                                                 'start': -0.9},
                                       'yaxis': 'y1'}
            self.assertEqual(dp['data'][0], expected_dp_data_hist_1)

            expected_dp_data_hist_2 = {'autobinx': False,
                                       'histnorm': 'probability density',
                                       'legendgroup': '2013',
                                       'marker':
                                       {'color': 'rgb(255, 127, 14)'},
                                       'name': '2013',
                                       'opacity': 0.7,
                                       'type': 'histogram',
                                       'x': [0.8, 1.5, 1.5, 0.6, 0.59, 1.0,
                                             0.8, 1.7, 0.5, 0.8, -0.3, 1.2,
                                             0.56, 0.3, 2.2],
                                       'xaxis': 'x1',
                                       'xbins': {'end': 2.2, 'size': 0.2,
                                                 'start': -0.3},
                                       'yaxis': 'y1'}
            self.assertEqual(dp['data'][1], expected_dp_data_hist_2)


class TestStreamline(TestCase):

    def test_wrong_arrow_scale(self):

        # check for ValueError if arrow_scale is <= 0

        kwargs = {'x': [0, 2], 'y': [0, 2],
                  'u': [[-1, -5], [-1, -5]],
                  'v': [[1, 1], [-3, -3]],
                  'arrow_scale': 0}
        self.assertRaises(ValueError, tls.FigureFactory.create_streamline,
                          **kwargs)

    def test_wrong_density(self):

        # check for ValueError if density is <= 0

        kwargs = {'x': [0, 2], 'y': [0, 2],
                  'u': [[-1, -5], [-1, -5]],
                  'v': [[1, 1], [-3, -3]],
                  'density': 0}
        self.assertRaises(ValueError, tls.FigureFactory.create_streamline,
                          **kwargs)

    def test_uneven_x(self):

        # check for PlotlyError if x is not evenly spaced

        kwargs = {'x': [0, 2, 7, 9], 'y': [0, 2, 4, 6],
                  'u': [[-1, -5], [-1, -5]],
                  'v': [[1, 1], [-3, -3]]}
        self.assertRaises(PlotlyError, tls.FigureFactory.create_streamline,
                          **kwargs)

    def test_uneven_y(self):

        # check for PlotlyError if y is not evenly spaced

        kwargs = {'x': [0, 2, 4, 6], 'y': [1.5, 2, 3, 3.5],
                  'u': [[-1, -5], [-1, -5]],
                  'v': [[1, 1], [-3, -3]]}
        self.assertRaises(PlotlyError, tls.FigureFactory.create_streamline,
                          **kwargs)

    def test_unequal_length_xy(self):

        # check for PlotlyError if u and v are not the same length

        kwargs = {'x': [0, 2, 4, 6], 'y': [1.5, 2, 3.5],
                  'u': [[-1, -5], [-1, -5]],
                  'v': [[1, 1], [-3, -3]]}
        self.assertRaises(PlotlyError, tls.FigureFactory.create_streamline,
                          **kwargs)

    def test_unequal_length_uv(self):

        # check for PlotlyError if u and v are not the same length

        kwargs = {'x': [0, 2, 4, 6], 'y': [1.5, 2, 3, 3.5],
                  'u': [[-1, -5], [-1, -5], [-1, -5]],
                  'v': [[1, 1], [-3, -3]]}
        self.assertRaises(PlotlyError, tls.FigureFactory.create_streamline,
                          **kwargs)

    def test_simple_streamline(self):

        # Need np to check streamline data,
        # this checks that the first 101 x and y values from streamline are
        # what we expect for a simple streamline where:
        # x = np.linspace(-1, 1, 3)
        # y = np.linspace(-1, 1, 3)
        # Y, X = np.meshgrid(x, y)
        # u = X**2
        # v = Y**2
        # u = u.T #transpose
        # v = v.T #transpose

        strln = tls.FigureFactory.create_streamline(x=[-1., 0., 1.],
                                                    y=[-1., 0., 1.],
                                                    u=[[1., 0., 1.],
                                                       [1., 0., 1.],
                                                       [1., 0., 1.]],
                                                    v=[[1., 1., 1.],
                                                       [0., 0., 0.],
                                                       [1., 1., 1.]])
        expected_strln_0_100 = {
            'y': [-1.0, -0.9788791845863757, -0.9579399744939614, -0.9371777642073374, -0.9165881396413338, -0.8961668671832106, -0.8759098835283448, -0.8558132862403048, -0.835873324973195, -0.8160863933003534, -0.7964490210989816, -0.7769578674451656, -0.7576097139780906, -0.7384014586961288, -0.7193301101509343, -0.7003927820087748, -0.681586687951103, -0.6629091368888596, -0.64435752846723, -0.6259293488396024, -0.6076221666912738, -0.5894336294951057, -0.5713614599827976, -0.5534034528167977, -0.5355574714490806, -0.5178214451541254, -0.5001933662244311, -0.4826712873178177, -0.4652533189465894, -0.44793762709939944, -0.4307224309873414, -0.4136060009064273, -0.39658665620919065, -0.3796627633786812, -0.3628327341986042, -0.34609502401380254, -0.3294481300756896, -0.31289058996761565, -0.2964209801054992, -0.28003791430937197, -0.2637400424417804, -0.24752604910925968, -0.23139465242334434, -0.21534460281781365, -0.19937468191908325, -0.18348370146685278, -0.1676705022823033, -0.15193395328130999, -0.13627295053029143, -0.1206864163424669, -0.10517329841242584, -0.08973256898704507, -0.07436322407090357, -0.05906428266445696, -0.04383478603333624, -0.028673797007230273, -0.013580399306900914, 0.0014484211645073852, 0.01648792568956914, 0.03159429687713278, 0.04676843461935776, 0.062011259175942746, 0.07732371182540754, 0.09270675554339824, 0.10816137570939799, 0.12368858084331191, 0.1392894033734846, 0.1549649004378033, 0.1707161547196483, 0.1865442753205595, 0.20245039867161063, 0.21843568948560943, 0.23450134175238246, 0.25064857977955146, 0.26687865928136767, 0.2831928685183458, 0.29959252949062387, 0.3160789991881776, 0.33265367090123643, 0.3493179755944802, 0.366073383348855, 0.3829214048751186, 0.39986359310352526, 0.41690154485438513, 0.4340369025945845, 0.4512713562855355, 0.46860664532844054, 0.4860445606132082, 0.5035869466778524, 0.5212357039857456, 0.5389927913286829, 0.5568602283643591, 0.5748400982975623, 0.5929345507151613, 0.6111458045858065, 0.6294761514361948, 0.6479279587167714, 0.6665036733708583, 0.6852058256224467, 0.704037032999252],
            'x': [-1.0, -0.9788791845863756, -0.9579399744939614, -0.9371777642073374, -0.9165881396413338, -0.8961668671832106, -0.8759098835283448, -0.8558132862403048, -0.835873324973195, -0.8160863933003534, -0.7964490210989816, -0.7769578674451656, -0.7576097139780906, -0.7384014586961289, -0.7193301101509344, -0.7003927820087748, -0.6815866879511031, -0.6629091368888596, -0.6443575284672302, -0.6259293488396025, -0.6076221666912739, -0.5894336294951058, -0.5713614599827976, -0.5534034528167978, -0.5355574714490807, -0.5178214451541254, -0.5001933662244312, -0.4826712873178177, -0.4652533189465894, -0.44793762709939944, -0.4307224309873414, -0.4136060009064273, -0.39658665620919065, -0.3796627633786812, -0.3628327341986042, -0.34609502401380254, -0.3294481300756896, -0.31289058996761565, -0.2964209801054992, -0.28003791430937197, -0.2637400424417804, -0.24752604910925968, -0.23139465242334434, -0.21534460281781365, -0.19937468191908325, -0.18348370146685278, -0.1676705022823033, -0.15193395328130999, -0.13627295053029143, -0.1206864163424669, -0.10517329841242584, -0.08973256898704507, -0.07436322407090357, -0.05906428266445696, -0.04383478603333624, -0.028673797007230273, -0.013580399306900914, 0.0014484211645073852, 0.01648792568956914, 0.03159429687713278, 0.04676843461935776, 0.062011259175942746, 0.07732371182540754, 0.09270675554339824, 0.10816137570939799, 0.12368858084331191, 0.1392894033734846, 0.1549649004378033, 0.1707161547196483, 0.1865442753205595, 0.20245039867161063, 0.21843568948560943, 0.23450134175238246, 0.25064857977955146, 0.26687865928136767, 0.2831928685183458, 0.29959252949062387, 0.3160789991881776, 0.33265367090123643, 0.3493179755944802, 0.366073383348855, 0.3829214048751186, 0.39986359310352526, 0.41690154485438513, 0.4340369025945845, 0.4512713562855355, 0.46860664532844054, 0.4860445606132082, 0.5035869466778524, 0.5212357039857456, 0.5389927913286829, 0.5568602283643591, 0.5748400982975623, 0.5929345507151613, 0.6111458045858065, 0.6294761514361948, 0.6479279587167714, 0.6665036733708583, 0.6852058256224467, 0.704037032999252],
            'type': 'scatter',
            'mode': 'lines'
        }
        self.assertListEqual(strln['data'][0]['y'][0:100],
                             expected_strln_0_100['y'])
        self.assertListEqual(strln['data'][0]['x'][0:100],
                             expected_strln_0_100['x'])


class TestDendrogram(NumpyTestUtilsMixin, TestCase):

    def test_default_dendrogram(self):
        X = np.array([[1, 2, 3, 4], [1, 1, 3, 4], [1, 2, 1, 4], [1, 2, 3, 1]])
        dendro = tls.FigureFactory.create_dendrogram(X=X)

        expected_dendro = go.Figure(
            data=go.Data([
                go.Scatter(
                    x=np.array([25., 25., 35., 35.]),
                    y=np.array([0., 1., 1., 0.]),
                    marker=go.Marker(color='rgb(61,153,112)'),
                    mode='lines',
                    xaxis='x',
                    yaxis='y'
                ),
                go.Scatter(
                    x=np.array([15., 15., 30., 30.]),
                    y=np.array([0., 2.23606798, 2.23606798, 1.]),
                    marker=go.Marker(color='rgb(61,153,112)'),
                    mode='lines',
                    xaxis='x',
                    yaxis='y'
                ),
                go.Scatter(
                    x=np.array([5., 5., 22.5, 22.5]),
                    y=np.array([0., 3.60555128, 3.60555128, 2.23606798]),
                    marker=go.Marker(color='rgb(0,116,217)'),
                    mode='lines',
                    xaxis='x',
                    yaxis='y'
                )
            ]),
            layout=go.Layout(
                autosize=False,
                height='100%',
                hovermode='closest',
                showlegend=False,
                width='100%',
                xaxis=go.XAxis(
                    mirror='allticks',
                    rangemode='tozero',
                    showgrid=False,
                    showline=True,
                    showticklabels=True,
                    tickmode='array',
                    ticks='outside',
                    ticktext=np.array(['3', '2', '0', '1']),
                    tickvals=[5.0, 15.0, 25.0, 35.0],
                    type='linear',
                    zeroline=False
                ),
                yaxis=go.YAxis(
                    mirror='allticks',
                    rangemode='tozero',
                    showgrid=False,
                    showline=True,
                    showticklabels=True,
                    ticks='outside',
                    type='linear',
                    zeroline=False
                )
            )
        )

        self.assertEqual(len(dendro['data']), 3)

        # this is actually a bit clearer when debugging tests.
        self.assert_dict_equal(dendro['data'][0], expected_dendro['data'][0])
        self.assert_dict_equal(dendro['data'][1], expected_dendro['data'][1])
        self.assert_dict_equal(dendro['data'][2], expected_dendro['data'][2])

        self.assert_dict_equal(dendro['layout'], expected_dendro['layout'])

    def test_dendrogram_random_matrix(self):

        # create a random uncorrelated matrix
        X = np.random.rand(5, 5)

        # variable 2 is correlated with all the other variables
        X[2, :] = sum(X, 0)

        names = ['Jack', 'Oxana', 'John', 'Chelsea', 'Mark']
        dendro = tls.FigureFactory.create_dendrogram(X, labels=names)

        expected_dendro = go.Figure(
            data=go.Data([
                go.Scatter(
                    marker=go.Marker(color='rgb(61,153,112)'),
                    mode='lines',
                    xaxis='x',
                    yaxis='y'
                ),
                go.Scatter(
                    marker=go.Marker(
                        color='rgb(61,153,112)'
                    ),
                    mode='lines',
                    xaxis='x',
                    yaxis='y'
                ),
                go.Scatter(
                    marker=go.Marker(color='rgb(61,153,112)'),
                    mode='lines',
                    xaxis='x',
                    yaxis='y'
                ),
                go.Scatter(
                    marker=go.Marker(color='rgb(0,116,217)'),
                    mode='lines',
                    xaxis='x',
                    yaxis='y'
                )
            ]),
            layout=go.Layout(
                autosize=False,
                height='100%',
                hovermode='closest',
                showlegend=False,
                width='100%',
                xaxis=go.XAxis(
                    mirror='allticks',
                    rangemode='tozero',
                    showgrid=False,
                    showline=True,
                    showticklabels=True,
                    tickmode='array',
                    ticks='outside',
                    tickvals=[5.0, 15.0, 25.0, 35.0, 45.0],
                    type='linear',
                    zeroline=False
                ),
                yaxis=go.YAxis(
                    mirror='allticks',
                    rangemode='tozero',
                    showgrid=False,
                    showline=True,
                    showticklabels=True,
                    ticks='outside',
                    type='linear',
                    zeroline=False
                )
            )
        )

        self.assertEqual(len(dendro['data']), 4)

        # it's random, so we can only check that the values aren't equal
        y_vals = [dendro['data'][0].pop('y'), dendro['data'][1].pop('y'),
                  dendro['data'][2].pop('y'), dendro['data'][3].pop('y')]
        for i in range(len(y_vals)):
            for j in range(len(y_vals)):
                if i != j:
                    self.assertFalse(np.allclose(y_vals[i], y_vals[j]))

        x_vals = [dendro['data'][0].pop('x'), dendro['data'][1].pop('x'),
                  dendro['data'][2].pop('x'), dendro['data'][3].pop('x')]
        for i in range(len(x_vals)):
            for j in range(len(x_vals)):
                if i != j:
                    self.assertFalse(np.allclose(x_vals[i], x_vals[j]))

        # we also need to check the ticktext manually
        xaxis_ticktext = dendro['layout']['xaxis'].pop('ticktext')
        self.assertEqual(xaxis_ticktext[0], 'John')

        # this is actually a bit clearer when debugging tests.
        self.assert_dict_equal(dendro['data'][0], expected_dendro['data'][0])
        self.assert_dict_equal(dendro['data'][1], expected_dendro['data'][1])
        self.assert_dict_equal(dendro['data'][2], expected_dendro['data'][2])
        self.assert_dict_equal(dendro['data'][3], expected_dendro['data'][3])

        self.assert_dict_equal(dendro['layout'], expected_dendro['layout'])

    def test_dendrogram_orientation(self):
        X = np.random.rand(5, 5)

        dendro_left = tls.FigureFactory.create_dendrogram(
                       X, orientation='left')
        self.assertEqual(len(dendro_left['layout']['yaxis']['ticktext']), 5)
        tickvals_left = np.array(dendro_left['layout']['yaxis']['tickvals'])
        self.assertTrue((tickvals_left <= 0).all())

        dendro_right = tls.FigureFactory.create_dendrogram(
                        X, orientation='right')
        tickvals_right = np.array(dendro_right['layout']['yaxis']['tickvals'])
        self.assertTrue((tickvals_right >= 0).all())

        dendro_bottom = tls.FigureFactory.create_dendrogram(
                        X, orientation='bottom')
        self.assertEqual(len(dendro_bottom['layout']['xaxis']['ticktext']), 5)
        tickvals_bottom = np.array(
            dendro_bottom['layout']['xaxis']['tickvals']
        )
        self.assertTrue((tickvals_bottom >= 0).all())

        dendro_top = tls.FigureFactory.create_dendrogram(X, orientation='top')
        tickvals_top = np.array(dendro_top['layout']['xaxis']['tickvals'])
        self.assertTrue((tickvals_top <= 0).all())

    def test_dendrogram_colorscale(self):
        X = np.array([[1, 2, 3, 4],
                      [1, 1, 3, 4],
                      [1, 2, 1, 4],
                      [1, 2, 3, 1]])
        greyscale = [
                'rgb(0,0,0)',  # black
                'rgb(05,105,105)',  # dim grey
                'rgb(128,128,128)',  # grey
                'rgb(169,169,169)',  # dark grey
                'rgb(192,192,192)',  # silver
                'rgb(211,211,211)',  # light grey
                'rgb(220,220,220)',  # gainsboro
                'rgb(245,245,245)']  # white smoke

        dendro = tls.FigureFactory.create_dendrogram(X, colorscale=greyscale)

        expected_dendro = go.Figure(
            data=go.Data([
                go.Scatter(
                    x=np.array([25., 25., 35., 35.]),
                    y=np.array([0., 1., 1., 0.]),
                    marker=go.Marker(color='rgb(128,128,128)'),
                    mode='lines',
                    xaxis='x',
                    yaxis='y'
                ),
                go.Scatter(
                    x=np.array([15., 15., 30., 30.]),
                    y=np.array([0., 2.23606798, 2.23606798, 1.]),
                    marker=go.Marker(color='rgb(128,128,128)'),
                    mode='lines',
                    xaxis='x',
                    yaxis='y'
                ),
                go.Scatter(
                    x=np.array([5., 5., 22.5, 22.5]),
                    y=np.array([0., 3.60555128, 3.60555128, 2.23606798]),
                    marker=go.Marker(color='rgb(0,0,0)'),
                    mode='lines',
                    xaxis='x',
                    yaxis='y'
                )
            ]),
            layout=go.Layout(
                autosize=False,
                height='100%',
                hovermode='closest',
                showlegend=False,
                width='100%',
                xaxis=go.XAxis(
                    mirror='allticks',
                    rangemode='tozero',
                    showgrid=False,
                    showline=True,
                    showticklabels=True,
                    tickmode='array',
                    ticks='outside',
                    ticktext=np.array(['3', '2', '0', '1']),
                    tickvals=[5.0, 15.0, 25.0, 35.0],
                    type='linear',
                    zeroline=False
                ),
                yaxis=go.YAxis(
                    mirror='allticks',
                    rangemode='tozero',
                    showgrid=False,
                    showline=True,
                    showticklabels=True,
                    ticks='outside',
                    type='linear',
                    zeroline=False
                )
            )
        )

        self.assertEqual(len(dendro['data']), 3)

        # this is actually a bit clearer when debugging tests.
        self.assert_dict_equal(dendro['data'][0], expected_dendro['data'][0])
        self.assert_dict_equal(dendro['data'][1], expected_dendro['data'][1])
        self.assert_dict_equal(dendro['data'][2], expected_dendro['data'][2])


class TestTrisurf(NumpyTestUtilsMixin, TestCase):

    def test_vmin_and_vmax(self):

        # check if vmin is greater than or equal to vmax
        u = np.linspace(0, 2, 2)
        v = np.linspace(0, 2, 2)
        u, v = np.meshgrid(u, v)
        u = u.flatten()
        v = v.flatten()

        x = u
        y = v
        z = u*v

        points2D = np.vstack([u, v]).T
        tri = Delaunay(points2D)
        simplices = tri.simplices

        pattern = (
            "Incorrect relation between vmin and vmax. The vmin value cannot "
            "be bigger than or equal to the value of vmax."
        )

        self.assertRaisesRegexp(PlotlyError, pattern,
                                tls.FigureFactory.create_trisurf,
                                x, y, z, simplices)

    def test_valid_colormap(self):

        # create data for trisurf plot
        u = np.linspace(-np.pi, np.pi, 3)
        v = np.linspace(-np.pi, np.pi, 3)
        u, v = np.meshgrid(u, v)
        u = u.flatten()
        v = v.flatten()

        x = u
        y = u*np.cos(v)
        z = u*np.sin(v)

        points2D = np.vstack([u, v]).T
        tri = Delaunay(points2D)
        simplices = tri.simplices

        # check that a valid plotly colorscale name is entered
        self.assertRaises(PlotlyError, tls.FigureFactory.create_trisurf,
                          x, y, z, simplices, colormap='foo')

        # check that colormap is a list, if not a string

        pattern1 = (
            "If 'colormap' is a list, then its items must be tripets of the "
            "form a,b,c or 'rgbx,y,z' where a,b,c are between 0 and 1 "
            "inclusive and x,y,z are between 0 and 255 inclusive."
        )

        self.assertRaisesRegexp(PlotlyError, pattern1,
                                tls.FigureFactory.create_trisurf,
                                x, y, z, simplices, colormap=3)

        # check: if colormap is a list of rgb color strings, make sure the
        # entries of each color are no greater than 255.0

        pattern2 = (
            "Whoops! The elements in your rgb colormap tuples "
            "cannot exceed 255.0."
        )

        self.assertRaisesRegexp(PlotlyError, pattern2,
                                tls.FigureFactory.create_trisurf,
                                x, y, z, simplices,
                                colormap=['rgb(1, 2, 3)', 'rgb(4, 5, 600)'])

        # check: if colormap is a list of tuple colors, make sure the entries
        # of each tuple are no greater than 1.0

        pattern3 = (
            "Whoops! The elements in your rgb colormap tuples "
            "cannot exceed 1.0."
        )

        self.assertRaisesRegexp(PlotlyError, pattern3,
                                tls.FigureFactory.create_trisurf,
                                x, y, z, simplices,
                                colormap=[(0.2, 0.4, 0.6), (0.8, 1.0, 1.2)])

    def test_trisurf_all_args(self):

        # check if trisurf plot matches with expected output
        u = np.linspace(-1, 1, 3)
        v = np.linspace(-1, 1, 3)
        u, v = np.meshgrid(u, v)
        u = u.flatten()
        v = v.flatten()

        x = u
        y = v
        z = u*v

        points2D = np.vstack([u, v]).T
        tri = Delaunay(points2D)
        simplices = tri.simplices

        test_trisurf_plot = tls.FigureFactory.create_trisurf(
            x, y, z, simplices
        )

        exp_trisurf_plot = {
        'data': [
            {
                'facecolor': ['rgb(143.0, 123.0, 97.0)',
                              'rgb(255.0, 127.0, 14.0)',
                              'rgb(143.0, 123.0, 97.0)',
                              'rgb(31.0, 119.0, 180.0)',
                              'rgb(143.0, 123.0, 97.0)',
                              'rgb(31.0, 119.0, 180.0)',
                              'rgb(143.0, 123.0, 97.0)',
                              'rgb(255.0, 127.0, 14.0)'],
                'i': [3, 1, 1, 5, 7, 3, 5, 7],
                'j': [1, 3, 5, 1, 3, 7, 7, 5],
                'k': [4, 0, 4, 2, 4, 6, 4, 8],
                'name': '',
                'type': 'mesh3d',
                'x': np.array([-1.,  0.,  1., -1.,  0.,  1., -1.,  0.,  1.]),
                'y': np.array([-1., -1., -1.,  0.,  0.,  0.,  1.,  1.,  1.]),
                'z': np.array([ 1., -0., -1., -0.,  0.,  0., -1.,  0.,  1.])
            },
            {
                'line': {'color': 'rgb(50, 50, 50)', 'width': 1.5},
                'mode': 'lines',
                'type': 'scatter3d',
                'x': [-1.0, 0.0, 0.0, -1.0, None, 0.0, -1.0, -1.0, 0.0, None,
                      0.0, 1.0, 0.0, 0.0, None, 1.0, 0.0, 1.0, 1.0, None, 0.0,
                      -1.0, 0.0, 0.0, None, -1.0, 0.0, -1.0, -1.0, None, 1.0,
                      0.0, 0.0, 1.0, None, 0.0, 1.0, 1.0, 0.0, None],
                'y': [0.0, -1.0, 0.0, 0.0, None, -1.0, 0.0, -1.0, -1.0, None,
                      -1.0, 0.0, 0.0, -1.0, None, 0.0, -1.0, -1.0, 0.0, None,
                      1.0, 0.0, 0.0, 1.0, None, 0.0, 1.0, 1.0, 0.0, None, 0.0,
                      1.0, 0.0, 0.0, None, 1.0, 0.0, 1.0, 1.0, None],
                'z': [-0.0, -0.0, 0.0, -0.0, None, -0.0, -0.0, 1.0, -0.0,
                      None, -0.0, 0.0, 0.0, -0.0, None, 0.0, -0.0, -1.0, 0.0,
                      None, 0.0, -0.0, 0.0, 0.0, None, -0.0, 0.0, -1.0, -0.0,
                      None, 0.0, 0.0, 0.0, 0.0, None, 0.0, 0.0, 1.0, 0.0, None]
            }
        ],
        'layout': {
            'height': 800,
            'scene': {'aspectratio': {'x': 1, 'y': 1, 'z': 1},
            'xaxis': {'backgroundcolor': 'rgb(230, 230, 230)',
            'gridcolor': 'rgb(255, 255, 255)',
            'showbackground': True,
            'zerolinecolor': 'rgb(255, 255, 255)'},
            'yaxis': {'backgroundcolor': 'rgb(230, 230, 230)',
            'gridcolor': 'rgb(255, 255, 255)',
            'showbackground': True,
            'zerolinecolor': 'rgb(255, 255, 255)'},
            'zaxis': {'backgroundcolor': 'rgb(230, 230, 230)',
            'gridcolor': 'rgb(255, 255, 255)',
            'showbackground': True,
            'zerolinecolor': 'rgb(255, 255, 255)'}},
            'title': 'Trisurf Plot',
            'width': 800
        }
        }

        self.assert_dict_equal(test_trisurf_plot['layout'],
                               exp_trisurf_plot['layout'])

        self.assert_dict_equal(test_trisurf_plot['data'][0],
                               exp_trisurf_plot['data'][0])

        self.assert_dict_equal(test_trisurf_plot['data'][1],
                               exp_trisurf_plot['data'][1])


class TestScatterPlotMatrix(NumpyTestUtilsMixin, TestCase):

    def test_dataframe_input(self):

        # check: dataframe is imported
        df = 'foo'

        pattern = (
            "Dataframe not inputed. Please use a pandas dataframe to produce "
            "a scatterplot matrix."
        )

        self.assertRaisesRegexp(PlotlyError, pattern,
                                tls.FigureFactory.create_scatterplotmatrix,
                                df)

    def test_one_column_dataframe(self):

        # check: dataframe has 1 column or less
        df = pd.DataFrame([1, 2, 3])

        pattern = (
            "Dataframe has only one column. To use the scatterplot matrix, "
            "use at least 2 columns."
        )

        self.assertRaisesRegexp(PlotlyError, pattern,
                                tls.FigureFactory.create_scatterplotmatrix,
                                df)

    def test_valid_diag_choice(self):

        # make sure that the diagonal param is valid
        df = pd.DataFrame([[1, 2, 3], [4, 5, 6]])

        self.assertRaises(PlotlyError,
                          tls.FigureFactory.create_scatterplotmatrix,
                          df, diag='foo')

    def test_forbidden_params(self):

        # check: the forbidden params of 'marker' in **kwargs
        df = pd.DataFrame([[1, 2, 3], [4, 5, 6]])

        kwargs = {'marker': {'size': 15}}

        pattern = (
            "Your kwargs dictionary cannot include the 'size', 'color' or "
            "'colorscale' key words inside the marker dict since 'size' is "
            "already an argument of the scatterplot matrix function and both "
            "'color' and 'colorscale are set internally."
        )

        self.assertRaisesRegexp(PlotlyError, pattern,
                                tls.FigureFactory.create_scatterplotmatrix,
                                df, **kwargs)

    def test_valid_index_choice(self):

        # check: index is a column name
        df = pd.DataFrame([[1, 2], [3, 4]], columns=['apple', 'pear'])

        pattern = (
            "Make sure you set the index input variable to one of the column "
            "names of your dataframe."
        )

        self.assertRaisesRegexp(PlotlyError, pattern,
                                tls.FigureFactory.create_scatterplotmatrix,
                                df, index='grape')

    def test_same_data_in_dataframe_columns(self):

        # check: either all numbers or strings in each dataframe column
        df = pd.DataFrame([['a', 2], [3, 4]])

        pattern = (
            "Error in dataframe. Make sure all entries of each column are "
            "either numbers or strings."
        )

        self.assertRaisesRegexp(PlotlyError, pattern,
                                tls.FigureFactory.create_scatterplotmatrix,
                                df)

        df = pd.DataFrame([[1, 2], ['a', 4]])

        self.assertRaisesRegexp(PlotlyError, pattern,
                                tls.FigureFactory.create_scatterplotmatrix,
                                df)

    def test_same_data_in_index(self):

        # check: either all numbers or strings in index column
        df = pd.DataFrame([['a', 2], [3, 4]], columns=['apple', 'pear'])

        pattern = (
            "Error in indexing column. Make sure all entries of each column "
            "are all numbers or all strings."
        )

        self.assertRaisesRegexp(PlotlyError, pattern,
                                tls.FigureFactory.create_scatterplotmatrix,
                                df, index='apple')

        df = pd.DataFrame([[1, 2], ['a', 4]], columns=['apple', 'pear'])

        self.assertRaisesRegexp(PlotlyError, pattern,
                                tls.FigureFactory.create_scatterplotmatrix,
                                df, index='apple')

    def test_valid_palette(self):

        # check: the palette argument is in a acceptable form
        df = pd.DataFrame([[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                          columns=['a', 'b', 'c'])

        self.assertRaisesRegexp(PlotlyError, "You must pick a valid "
                                             "plotly colorscale name.",
                                tls.FigureFactory.create_scatterplotmatrix,
                                df, use_theme=True, index='a',
                                palette='fake_scale')

        pattern = (
            "The items of 'palette' must be tripets of the form a,b,c or "
            "'rgbx,y,z' where a,b,c belong to the interval 0,1 and x,y,z "
            "belong to 0,255."
        )

        self.assertRaisesRegexp(PlotlyError, pattern,
                                tls.FigureFactory.create_scatterplotmatrix,
                                df, use_theme=True, palette=1, index='c')

    def test_valid_endpts(self):

        # check: the endpts is a list or a tuple
        df = pd.DataFrame([[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                          columns=['a', 'b', 'c'])

        pattern = (
            "The intervals_endpts argument must be a list or tuple of a "
            "sequence of increasing numbers."
        )

        self.assertRaisesRegexp(PlotlyError, pattern,
                                tls.FigureFactory.create_scatterplotmatrix,
                                df, use_theme=True, index='a',
                                palette='Blues', endpts='foo')

        # check: the endpts are a list of numbers
        self.assertRaisesRegexp(PlotlyError, pattern,
                                tls.FigureFactory.create_scatterplotmatrix,
                                df, use_theme=True, index='a',
                                palette='Blues', endpts=['a'])

        # check: endpts is a list of INCREASING numbers
        self.assertRaisesRegexp(PlotlyError, pattern,
                                tls.FigureFactory.create_scatterplotmatrix,
                                df, use_theme=True, index='a',
                                palette='Blues', endpts=[2, 1])

    def test_scatter_plot_matrix(self):

        # check if test scatter plot matrix without index or theme matches
        # with the expected output
        df = pd.DataFrame([[2, 'Apple'], [6, 'Pear'],
                          [-15, 'Apple'], [5, 'Pear'],
                          [-2, 'Apple'], [0, 'Apple']],
                          columns=['Numbers', 'Fruit'])

        test_scatter_plot_matrix = tls.FigureFactory.create_scatterplotmatrix(
            df=df, diag='scatter', height=1000, width=1000, size=13,
            title='Scatterplot Matrix', use_theme=False
        )

        exp_scatter_plot_matrix = {
            'data': [{'marker': {'size': 13},
                      'mode': 'markers',
                      'showlegend': False,
                      'type': 'scatter',
                      'x': [2, 6, -15, 5, -2, 0],
                      'xaxis': 'x1',
                      'y': [2, 6, -15, 5, -2, 0],
                      'yaxis': 'y1'},
                     {'marker': {'size': 13},
                      'mode': 'markers',
                      'showlegend': False,
                      'type': 'scatter',
                      'x': ['Apple',
                            'Pear',
                            'Apple',
                            'Pear',
                            'Apple',
                            'Apple'],
                      'xaxis': 'x2',
                      'y': [2, 6, -15, 5, -2, 0],
                      'yaxis': 'y2'},
                     {'marker': {'size': 13},
                      'mode': 'markers',
                      'showlegend': False,
                      'type': 'scatter',
                      'x': [2, 6, -15, 5, -2, 0],
                      'xaxis': 'x3',
                      'y': ['Apple',
                            'Pear',
                            'Apple',
                            'Pear',
                            'Apple',
                            'Apple'],
                      'yaxis': 'y3'},
                     {'marker': {'size': 13},
                      'mode': 'markers',
                      'showlegend': False,
                      'type': 'scatter',
                      'x': ['Apple',
                            'Pear',
                            'Apple',
                            'Pear',
                            'Apple',
                            'Apple'],
                      'xaxis': 'x4',
                      'y': ['Apple', 'Pear', 'Apple', 'Pear', 'Apple', 'Apple'],
                      'yaxis': 'y4'}],
            'layout': {'height': 1000,
                       'showlegend': True,
                       'title': 'Scatterplot Matrix',
                       'width': 1000,
                       'xaxis1': {'anchor': 'y1',
                                  'domain': [0.0, 0.45]},
                       'xaxis2': {'anchor': 'y2',
                                  'domain': [0.55, 1.0]},
                       'xaxis3': {'anchor': 'y3',
                                  'domain': [0.0, 0.45], 'title': 'Numbers'},
                       'xaxis4': {'anchor': 'y4',
                                  'domain': [0.55, 1.0], 'title': 'Fruit'},
                       'yaxis1': {'anchor': 'x1',
                                  'domain': [0.575, 1.0], 'title': 'Numbers'},
                       'yaxis2': {'anchor': 'x2',
                                  'domain': [0.575, 1.0]},
                       'yaxis3': {'anchor': 'x3',
                                  'domain': [0.0, 0.425], 'title': 'Fruit'},
                       'yaxis4': {'anchor': 'x4',
                                  'domain': [0.0, 0.425]}}
        }

        self.assert_dict_equal(test_scatter_plot_matrix['data'][0],
                               exp_scatter_plot_matrix['data'][0])

        self.assert_dict_equal(test_scatter_plot_matrix['data'][1],
                               exp_scatter_plot_matrix['data'][1])

        self.assert_dict_equal(test_scatter_plot_matrix['layout'],
                               exp_scatter_plot_matrix['layout'])

    def test_scatter_plot_matrix_kwargs(self):

        # check if test scatter plot matrix matches with
        # the expected output
        df = pd.DataFrame([[2, 'Apple'], [6, 'Pear'],
                          [-15, 'Apple'], [5, 'Pear'],
                          [-2, 'Apple'], [0, 'Apple']],
                          columns=['Numbers', 'Fruit'])

        test_scatter_plot_matrix = tls.FigureFactory.create_scatterplotmatrix(
            df, index='Fruit', endpts=[-10, -1], diag='histogram',
            height=1000, width=1000, size=13, title='Scatterplot Matrix',
            use_theme=True, palette='YlOrRd', marker=dict(symbol=136)
        )

        exp_scatter_plot_matrix = {
            'data': [{'marker': {'color': 'rgb(128.0, 0.0, 38.0)'},
                      'showlegend': False,
                      'type': 'histogram',
                      'x': [2, -15, -2, 0],
                      'xaxis': 'x1',
                      'yaxis': 'y1'},
                     {'marker': {'color': 'rgb(255.0, 255.0, 204.0)'},
                      'showlegend': False,
                      'type': 'histogram',
                      'x': [6, 5],
                      'xaxis': 'x1',
                      'yaxis': 'y1'}],
            'layout': {'barmode': 'stack',
                       'height': 1000,
                       'showlegend': True,
                       'title': 'Scatterplot Matrix',
                       'width': 1000,
                       'xaxis1': {'anchor': 'y1',
                                  'domain': [0.0, 1.0],
                                  'title': 'Numbers'},
                       'yaxis1': {'anchor': 'x1',
                                  'domain': [0.0, 1.0],
                                  'title': 'Numbers'}}
        }

        self.assert_dict_equal(test_scatter_plot_matrix['data'][0],
                               exp_scatter_plot_matrix['data'][0])

        self.assert_dict_equal(test_scatter_plot_matrix['data'][1],
                               exp_scatter_plot_matrix['data'][1])

        self.assert_dict_equal(test_scatter_plot_matrix['layout'],
                               exp_scatter_plot_matrix['layout'])


class TestGantt(NumpyTestUtilsMixin, TestCase):

    def test_df_dataframe(self):

        # validate df when it is a dataframe

        df1 = pd.DataFrame([[2, 'Apple']], columns=['Numbers', 'Fruit'])
        self.assertRaises(PlotlyError, tls.FigureFactory.create_gantt, df1)

        df2 = pd.DataFrame([['Job A', '2009-01-01', '2009-02-30', 25],
                            ['Job B', '2009-01-01', '2009-02-30', '25']],
                           columns=['Task', 'Start', 'Finish', 'Complete'])
        self.assertRaisesRegexp(PlotlyError,
                                "The values in the 'Complete' column must "
                                "be between 0 and 100.",
                                tls.FigureFactory.create_gantt, df2)

    def test_df_list(self):

        # validate df when it is a list

        df1 = 42
        self.assertRaisesRegexp(PlotlyError,
                                "You must input either a dataframe or a list "
                                "of dictionaries.",
                                tls.FigureFactory.create_gantt, df1)

        df2 = []
        self.assertRaisesRegexp(PlotlyError,
                                "Your list is empty. It must contain "
                                "at least one dictionary.",
                                tls.FigureFactory.create_gantt, df2)

        df3 = [42]
        self.assertRaisesRegexp(PlotlyError,
                                "Your list must only include dictionaries.",
                                tls.FigureFactory.create_gantt, df3)

        df4 = [{'apple': 2}]
        self.assertRaises(PlotlyError, tls.FigureFactory.create_gantt, df4)

        df5 = [{'Task': 'A Job',
                'Start': '2009-01-01',
                'Finish': '2009-02-30'},
               {'Task': 'A Job',
                'Start': '2009-01-01',
                'Finish': '2009-02-30',
                'Complete': 25}]
        self.assertRaisesRegexp(PlotlyError,
                                "If you are using 'Complete' as a dictionary "
                                "key, make sure each dictionary has this key "
                                "with an assigned value between 0 and 100.",
                                tls.FigureFactory.create_gantt, df5)

        df6 = [{'Task': 'A Job',
                'Start': '2009-01-01',
                'Finish': '2009-02-30',
                'Complete': 55},
               {'Task': 'A Job',
                'Start': '2009-01-01',
                'Finish': '2009-02-30',
                'Complete': 'string'}]
        self.assertRaisesRegexp(PlotlyError,
                                "The values in the 'Complete' column must "
                                "be between 0 and 100.",
                                tls.FigureFactory.create_gantt, df6)

    def test_valid_colors(self):

      # check: if color choices are valid

        df = [{'Task': 'A Job',
               'Start': '2009-01-01',
               'Finish': '2009-02-30',
               'Complete': 55},
              {'Task': 'A Job',
               'Start': '2009-01-01',
               'Finish': '2009-02-30',
               'Complete': 65}]

        self.assertRaises(PlotlyError, tls.FigureFactory.create_gantt,
                          df, colors='Weird')

        pattern1 = (
            "If 'colors' is a list then its items must be tripets of the "
            "form a,b,c or 'rgbx,y,z' where a,b,c are between 0 and 1 "
            "inclusive and x,y,z are between 0 and 255 inclusive."
        )

        self.assertRaisesRegexp(PlotlyError, pattern1,
                                tls.FigureFactory.create_gantt, df, colors=25)

        pattern2 = (
            "Whoops! The elements in your rgb colors tuples "
            "cannot exceed 255.0."
        )

        self.assertRaisesRegexp(PlotlyError, pattern2,
                                tls.FigureFactory.create_gantt, df,
                                colors=['rgb(1, 2, 3)', 'rgb(300, 2, 3)'])

        pattern3 = (
            "Whoops! The elements in your rgb colors tuples "
            "cannot exceed 1.0."
        )

        self.assertRaisesRegexp(PlotlyError, pattern3,
                                tls.FigureFactory.create_gantt, df,
                                colors=[(0.1, 0.2, 0.3), (0.6, 0.8, 1.2)])

    def test_use_colorscale(self):

        # checks: 'Complete' in inputted array or list

        df = [{'Task': 'A Job',
               'Start': '2009-01-01',
               'Finish': '2009-02-30'},
              {'Task': 'A Job',
               'Start': '2009-01-01',
               'Finish': '2009-02-30'}]

        pattern = (
            "In order to use colorscale there must be a "
            "'Complete' column in the chart."
        )
        self.assertRaisesRegexp(PlotlyError, pattern,
                                tls.FigureFactory.create_gantt, df,
                                use_colorscale=True)

    def test_gantt_all_args(self):

        # check if gantt chart matches with expected output

        df = [dict(Task="Run",
                   Start='2010-01-01',
                   Finish='2011-02-02',
                   Complete=0),
              dict(Task="Fast",
                   Start='2011-01-01',
                   Finish='2012-06-05',
                   Complete=25)]

        test_gantt_chart = tls.FigureFactory.create_gantt(
            df, colors='Blues', use_colorscale=True, reverse_colors=True,
            title='Title', bar_width=0.5, showgrid_x=True, showgrid_y=True,
            height=500, width=500
        )

        exp_gantt_chart = {
            'data': [{'marker': {'color': 'white'},
                      'name': '',
                      'x': ['2010-01-01', '2011-02-02'],
                      'y': [0, 0]},
                     {'marker': {'color': 'white'},
                      'name': '',
                      'x': ['2011-01-01', '2012-06-05'],
                      'y': [1, 1]}],
            'layout': {'height': 500,
                       'hovermode': 'closest',
                       'shapes': [{'fillcolor': 'rgb(220.0, 220.0, 220.0)',
                                   'line': {'width': 0},
                                   'opacity': 1,
                                   'type': 'rect',
                                   'x0': '2010-01-01',
                                   'x1': '2011-02-02',
                                   'xref': 'x',
                                   'y0': -0.5,
                                   'y1': 0.5,
                                   'yref': 'y'},
                                  {'fillcolor': 'rgb(166.25, 167.5, 208.0)',
                                   'line': {'width': 0},
                                   'opacity': 1,
                                   'type': 'rect',
                                   'x0': '2011-01-01',
                                   'x1': '2012-06-05',
                                   'xref': 'x',
                                   'y0': 0.5,
                                   'y1': 1.5,
                                   'yref': 'y'}],
                       'showlegend': False,
                       'title': 'Title',
                       'width': 500,
                       'xaxis': {
                           'rangeselector': {
                               'buttons': [{'count': 7, 'label': '1w',
                                            'step': 'day',
                                            'stepmode': 'backward'},
                                           {'count': 1, 'label': '1m',
                                            'step': 'month',
                                            'stepmode': 'backward'},
                                           {'count': 6, 'label': '6m',
                                            'step': 'month',
                                            'stepmode': 'backward'},
                                           {'count': 1, 'label': 'YTD',
                                            'step': 'year',
                                            'stepmode': 'todate'},
                                           {'count': 1, 'label': '1y',
                                            'step': 'year',
                                            'stepmode': 'backward'},
                                           {'step': 'all'}]
                           },
                           'showgrid': True,
                           'type': 'date',
                           'zeroline': False},
                       'yaxis': {'autorange': False,
                                 'range': [-1, 3],
                                 'showgrid': True,
                                 'ticktext': ['Run', 'Fast'],
                                 'tickvals': [0, 1],
                                 'zeroline': False}}
        }

        self.assert_dict_equal(test_gantt_chart['data'][0],
                               exp_gantt_chart['data'][0])

        self.assert_dict_equal(test_gantt_chart['data'][1],
                               exp_gantt_chart['data'][1])

        self.assert_dict_equal(test_gantt_chart['layout'],
                               exp_gantt_chart['layout'])
