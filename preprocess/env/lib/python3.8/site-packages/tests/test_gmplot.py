import unittest
import warnings
from gmplot.utility import StringIO
from gmplot.writer import _Writer
from gmplot.gmplot import _format_LatLng, _Route, GoogleMapPlotter, InvalidSymbolError

class GMPlotTest(unittest.TestCase):
    def test_format_LatLng(self):
        self.assertEqual(_format_LatLng(45.123456, -80.987654), 'new google.maps.LatLng(45.123456, -80.987654)')
        self.assertEqual(_format_LatLng(45.123456, -80.987654, 4), 'new google.maps.LatLng(45.1235, -80.9877)')
        self.assertEqual(_format_LatLng(45.1, -80.9, 3), 'new google.maps.LatLng(45.100, -80.900)')

# Note: This test only ensures that Route's functions can be called without failing,
#       it doesn't test if the resulting output can actually be rendered properly in a browser.
class RouteTest(unittest.TestCase):
    def test_write(self):
        route = _Route((37.770776,-122.461689), (37.780776,-122.461689))

        with StringIO() as f:
            with _Writer(f) as writer:
                route.write(writer)

    def test_write_waypoints(self):
        route = _Route((37.770776,-122.461689), (37.780776,-122.461689), waypoints=[(37.431257,-122.133121)])

        with StringIO() as f:
            with _Writer(f) as writer:
                route.write(writer)

# Note: This test only ensures that GoogleMapPlotter's functions can be called without failing,
#       it doesn't test if the resulting map can actually be rendered properly in a browser.
class GoogleMapPlotterTest(unittest.TestCase):
    PATH_1 = [(37.429, 37.428, 37.427, 37.427, 37.427),
            (-122.145, -122.145, -122.145, -122.146, -122.146)]
    PATH_2 = [[i+.01 for i in PATH_1[0]], [i+.02 for i in PATH_1[1]]]
    PATH_3 = [(37.433302, 37.431257, 37.427644, 37.430303), (-122.14488, -122.133121, -122.137799, -122.148743)]
    PATH_4 = [(37.423074, 37.422700, 37.422410, 37.422188, 37.422274, 37.422495, 37.422962, 37.423552, 37.424387, 37.425920, 37.425937),
        (-122.150288, -122.149794, -122.148936, -122.148142, -122.146747, -122.14561, -122.144773, -122.143936, -122.142992, -122.147863, -122.145953)]

    def test_get(self):
        bounds = {'north':37.832285, 'south': 37.637336, 'west': -122.520364, 'east': -122.346922}
        map = GoogleMapPlotter(37.428, -122.145, 16, fit_bounds=bounds)

        # Test marker:
        map.marker(37.427, -122.145, "yellow")
        map.marker(37.428, -122.146, "cornflowerblue")
        map.marker(37.429, -122.144, "k", title='Here')
        map.marker(37.430, -122.142, "red", label='A')

        # Test circle:
        map.circle(37.429, -122.145, 100, "#FF0000", ew=2)

        # Test plot:
        map.plot(self.PATH_1[0], self.PATH_1[1], "plum", edge_width=10)
        map.plot(self.PATH_2[0], self.PATH_2[1], "red")

        # Test directions:
        map.directions((37.770776,-122.461689), (37.780776,-122.461689), waypoints=[(37.431257,-122.133121)])

        # Test polygon:
        map.polygon(self.PATH_3[0], self.PATH_3[1], edge_color="cyan", edge_width=5, face_color="blue", face_alpha=0.1)

        # Test heatmap:
        map.heatmap(self.PATH_4[0], self.PATH_4[1], radius=40, weights=[1, 1, 1, 0.5, 0.5, 0.5, 1, 1, 1, 2, 2])

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            map.heatmap(self.PATH_3[0], self.PATH_3[1], threshold=10, radius=40, dissipating=False, gradient=[(30,30,30,0), (30,30,30,1), (50, 50, 50, 1)])

            self.assertEqual(len(w), 1, "'heatmap()' should raise a single warning")
            self.assertTrue(issubclass(w[-1].category, FutureWarning), "'heatmap()' should raise a 'FutureWarning'")

        # Test scatter:
        map.scatter(self.PATH_3[0], self.PATH_3[1], c='r', marker=[True, False, False, True])
        map.scatter(self.PATH_4[0], self.PATH_4[1], size=[1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2], symbol='x')
        map.scatter(self.PATH_4[0], self.PATH_4[1], s=90, marker=False, alpha=0.9, symbol='+', c='red', edge_width=4)
        map.scatter(self.PATH_3[0], self.PATH_3[1], 
            color=['r','g','b','k'],
            precision=[1,2,3,4],
            marker=[True, True, False, True],
            title=['First', 'Second', 'Third', 'Fourth'],
            label=['A','B','C','D'],
            size=[10,20,30,40],
            symbol=['+','o','x','x']
        )

        # Test ground overlay:
        bounds_dict = {'north':37.832285, 'south': 37.637336, 'west': -122.520364, 'east': -122.346922}
        map.ground_overlay('http://explore.museumca.org/creeks/images/TopoSFCreeks.jpg', bounds_dict, opacity=0.5)

        map.get()

    def test_scatter_length_mismatch(self):
        map = GoogleMapPlotter(37.428, -122.145, 16)

        with self.assertRaises(ValueError):
            map.scatter(self.PATH_3[0], self.PATH_3[1], 
                color=['r','g','b'],
                precision=[1,2],
                marker=[True],
                title=['First', 'Second'],
                label=['A','B','C','D','E'],
                size=[10,20],
                symbol=['+','o','x','x','o']
            )

    def test_invalid_symbol(self):
        map = GoogleMapPlotter(37.428, -122.145, 16)
        map.scatter(self.PATH_4[0], self.PATH_4[1], s=90, marker=False, alpha=0.9, symbol='z', c='red', edge_width=4)

        with self.assertRaises(InvalidSymbolError):
            map.get()

    def test_grid(self):
        map = GoogleMapPlotter(37.428, -122.145, 16)
        map.grid(37.42, 37.43, 0.001, -122.15, -122.14, 0.001)
        map.get()

    def test_map_styles(self):
        map_styles = [
            {
                'featureType': 'all',
                'stylers': [
                    {'saturation': -80},
                    {'lightness': 60},
                ]
            }
        ]

        map = GoogleMapPlotter(37.428, -122.145, 16, map_type='satellite', map_styles=map_styles, tilt=0, scale_control=True)
        map.get()

    def test_unsupported_marker_color(self):
        map = GoogleMapPlotter(37.428, -122.145, 16)
        map.marker(37.428, -122.146, "#123456") # (valid but unsupported color)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            map.get()
            
            self.assertEqual(len(w), 1, "'get()' should raise a single warning")
            self.assertTrue(issubclass(w[-1].category, UserWarning), "'get()' should raise a 'UserWarning'")
