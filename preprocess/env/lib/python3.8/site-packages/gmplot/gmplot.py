from __future__ import absolute_import

import json
import math
import os
import requests
import warnings
import math

from collections import namedtuple

from gmplot.color import _get_hex_color
from gmplot.google_maps_templates import SYMBOLS, CIRCLE_MARKER
from gmplot.utility import StringIO, _get_value, _get_embeddable_image, _INDENT_LEVEL
from gmplot.writer import _Writer

Symbol = namedtuple('Symbol', ['symbol', 'lat', 'long', 'size'])
# TODO: Rename `long` to `lng` to match the rest of the project (counts as an API change).

_ArgInfo = namedtuple('ArgInfo', ['arguments', 'default'])

class InvalidSymbolError(Exception):
    pass

class GoogleAPIError(Exception):
    pass

def safe_iter(var): # TODO: Remove since unused (counts as API change).
    try:
        return iter(var)
    except TypeError:
        return [var]

_COLOR_ICON_PATH = os.path.join(os.path.dirname(__file__), 'markers/%s.png')

def _format_LatLng(lat, lng, precision=6): # TODO: Make static method of GoogleMapPlotter.
    '''
    Format the given latitude/longitude location as a Google Maps LatLng object.

    Args:
        lat (float): Latitude.
        lng (float): Longitude.

    Optional:

    Args:
        precision (int): Number of digits after the decimal to round to for lat/lng values. Defaults to 6.

    Returns:
        str: Formatted Google Maps LatLng object.
    '''
    return 'new google.maps.LatLng(%.*f, %.*f)' % (precision, lat, precision, lng)

class _Route(object):
    '''For more info, see Google Maps' `Directions Service https://developers.google.com/maps/documentation/javascript/directions`_.'''
    
    def __init__(self, origin, destination, **kwargs):
        '''
        Args:
            origin ((float, float)): Origin, as a latitude/longitude tuple.
            destination ((float, float)): Destination, as a latitude/longitude tuple.

        Optional:

        Args:
            travel_mode (str): Travel mode. Defaults to 'DRIVING'.
            waypoints ([(float, float)]): Waypoints.
        '''
        self._origin = _format_LatLng(*origin)
        self._destination = _format_LatLng(*destination)
        self._travel_mode = _get_value(kwargs, ['travel_mode'], 'DRIVING').upper()
        self._waypoints = [_format_LatLng(*waypoint) for waypoint in _get_value(kwargs, ['waypoints'], [])]

    def write(self, w):
        '''
        Write the route.

        Args:
            w (_Writer): Writer used to write the route.
        '''
        w.write('new google.maps.DirectionsService().route({')
        w.indent()
        w.write('origin: %s,' % self._origin)
        w.write('destination: %s,' % self._destination)
        if self._waypoints:
            w.write('waypoints: [')
            w.indent()
            [w.write('{location: %s, stopover: false},' % waypoint) for waypoint in self._waypoints]
            w.dedent()
            w.write('],')
        w.write('travelMode: "%s"' % self._travel_mode)
        w.dedent()
        w.write('''  
            }, function(response, status) {
                if (status == google.maps.DirectionsStatus.OK) {
                    new google.maps.DirectionsRenderer({map: map}).setDirections(response);
                }
            });
        ''')
        w.write()

class _Text(object):
    '''For more info, see Google Maps' `Directions Service https://developers.google.com/maps/documentation/javascript/directions`_.'''
    
    def __init__(self, lat, lng, text, **kwargs):
        '''
        Args:
            lat (float): Latitude of the text label.
            lng (float): Longitude of the text label.
            text (str): Text to display.

        Optional:

        Args:
            color/c (str): Text color. Can be hex ('#00FFFF'), named ('cyan'), or matplotlib-like ('c'). Defaults to black.
        '''
        self._position = _format_LatLng(lat, lng)
        self._text = text
        self._color = _get_hex_color(_get_value(kwargs, ['color', 'c'], '#000000'))
        self._icon = _get_embeddable_image(_COLOR_ICON_PATH % 'clear')

    def write(self, w):
        '''
        Write the text.

        Args:
            w (_Writer): Writer used to write the text.
        '''
        w.write('new google.maps.Marker({')
        w.indent()
        w.write('label: {')
        w.indent()
        w.write('text: "%s",' % self._text)
        w.write('color: "%s",' % self._color)
        w.write('fontWeight: "bold"')
        w.dedent()
        w.write('},')
        w.write('icon: "%s",' % self._icon)
        w.write('position: %s,' % self._position)
        w.write('map: map')
        w.dedent()
        w.write('});')
        w.write()

class _MarkerIcon(object):
    def __init__(self, color):
        '''
        Args:
            color (str): Color of the marker icon.
        '''
        self._color = _get_hex_color(color)

        self.name = 'marker_icon_%s' % self._color[1:]
        '''str: JavaScript name of the marker icon.'''

        # Get this marker icon as an embeddable image:
        get_marker_icon_path = lambda color: _COLOR_ICON_PATH % color[1:]
        marker_icon_path = get_marker_icon_path(self._color)

        if not os.path.exists(marker_icon_path):
            warnings.warn(" Marker color '%s' isn't supported." % self._color)
            marker_icon_path = get_marker_icon_path('#000000')

        self._icon = _get_embeddable_image(marker_icon_path)

    def write(self, w, color_cache):
        '''
        Write the marker icon (if it isn't already written).

        Args:
            w (_Writer): Writer used to write the marker icon.
            color_cache (set): Cache of colors written so far.
        '''
        # If this marker icon hasn't been written before, then embed it in the script:
        if self._color not in color_cache:
            w.write('var %s = {' % self.name)
            w.indent()
            w.write('url: "%s",' % self._icon) 
            w.write('labelOrigin: new google.maps.Point(10, 11)') # TODO: Avoid hardcoded label origin.
            w.dedent()
            w.write('};')
            w.write()
            color_cache.add(self._color)

class _Marker(object):
    def __init__(self, position, **kwargs):
        '''
        Args:
            position (str): JavaScript code that represents the position of the marker.

        Optional:

        Args:
            name (str): JavaScript name of the marker.
            title (str): Hover-over title of the marker.
            label (str): Label displayed on the marker.
            icon (str): JavaScript code that represents the icon.
            draggable (bool): Whether or not the marker is draggable.
        '''
        self._position = position
        self._name = kwargs.get('name')
        self._title = kwargs.get('title')
        self._label = kwargs.get('label')
        self._icon = kwargs.get('icon')
        self._draggable = kwargs.get('draggable')

    def write(self, w):
        '''
        Write the marker.

        Args:
            w (_Writer): Writer used to write the marker.
        '''
        if self._name is not None: w.write('var %s = ' % self._name, end_in_newline=False)

        w.write('new google.maps.Marker({')
        w.indent()
        w.write('position: %s,' % self._position)

        if self._title is not None: w.write('title: "%s",' % self._title)
        if self._label is not None: w.write('label: "%s",' % self._label)
        if self._icon is not None: w.write('icon: %s,' % self._icon)
        if self._draggable is not None: w.write('draggable: %s,' % str(self._draggable).lower())

        w.write('map: map')
        w.dedent()
        w.write('});')
        w.write()

class _MarkerDropper(object):
    '''
    Handler that drops markers on map clicks.

    The markers can be deleted when clicked on.
    '''
    _MARKER_NAME = 'dropped_marker'
    _EVENT_OBJECT_NAME = 'event'

    def __init__(self, color, **kwargs):
        '''
        Args:
            color (str): Color of the markers to be dropped.

        Optional:

        Args:
            title (str): Hover-over title of the markers to be dropped.
            label (str): Label displayed on the markers to be dropped.
            draggable (bool): Whether or not the markers to be dropped are draggable.
        '''
        self._marker_icon = _MarkerIcon(color)
        self._marker = _Marker(
            '%s.latLng' % self._EVENT_OBJECT_NAME,
            name=self._MARKER_NAME,
            title=kwargs.get('title'),
            label=kwargs.get('label'),
            icon=self._marker_icon.name,
            draggable=kwargs.get('draggable')
        )

    def write(self, w, color_cache):
        '''
        Write the marker dropper.

        Args:
            w (_Writer): Writer used to write the marker dropper.
            color_cache (set): Cache of colors written so far.
        '''
        # Write the marker icon (if it isn't written already).
        self._marker_icon.write(w, color_cache)

        # Write the marker-dropping handler:
        w.write('map.addListener("click", function(%s) {' % self._EVENT_OBJECT_NAME)
        w.indent()
        self._marker.write(w)
        w.write('''
        {marker_name}.addListener('click', function() {{
            {marker_name}.setMap(null);
        }});
        '''.format(marker_name=self._MARKER_NAME))
        w.dedent()
        w.write('});')
        w.write()

class _MarkerInfoWindow(object):
    def __init__(self, marker_name, content):
        '''
        Args:
            marker_name (str): JavaScript name of the marker that should display this info window.
            content (str): HTML content to be displayed in this info window.
        '''
        self._marker_name = marker_name
        self._content = content

    def write(self, w, info_marker_index):
        '''
        Write the info window that attaches to the given marker on click.

        Args:
            w (_Writer): Writer used to write the info window.
            info_marker_index (int): Index of this info window.
        '''
        w.write('''
        var {info_window_name} = new google.maps.InfoWindow({{
            content: '{content}'
        }});

        {marker_name}.addListener('click', function() {{
            {info_window_name}.open(map, {marker_name});
        }});
        '''.format(
            info_window_name='info_window_%d' % info_marker_index,
            marker_name=self._marker_name,
            content=self._content.replace("'", "\\'").replace("\n", "\\n") # (escape single quotes and newlines)
        ))
        w.write()

class GoogleMapPlotter(object):
    '''
    Plotter that draws on a Google Map.
    '''

    _HEATMAP_DEFAULT_WEIGHT = 1

    def __init__(self, lat, lng, zoom, map_type='', apikey='', **kwargs):
        '''
        Args:
            lat (float): Latitude of the center of the map.
            lng (float): Longitude of the center of the map.
            zoom (int): `Zoom level`_, where 0 is fully zoomed out.

        Optional:

        Args:
            map_type (str): `Map type`_.
            apikey (str): Google Maps `API key`_.
            title (str): Title of the HTML file (as it appears in the browser tab).
            map_styles ([dict]): `Map styles`_. Requires `Maps JavaScript API`_.
            tilt (int): `Tilt`_ of the map upon zooming in.
            scale_control (bool): Whether or not to display the `scale control`_. Defaults to False.
            fit_bounds (dict): Fit the map to contain the given bounds, as a dict of the form
                ``{'north':, 'south':, 'east':, 'west':}``.
            
        .. _Zoom level: https://developers.google.com/maps/documentation/javascript/tutorial#zoom-levels
        .. _Map type: https://developers.google.com/maps/documentation/javascript/maptypes
        .. _API key: https://developers.google.com/maps/documentation/javascript/get-api-key
        .. _Map styles: https://developers.google.com/maps/documentation/javascript/style-reference
        .. _Maps JavaScript API: https://console.cloud.google.com/marketplace/details/google/maps-backend.googleapis.com
        .. _Tilt: https://developers.google.com/maps/documentation/javascript/reference/map#MapOptions.tilt
        .. _scale control: https://developers.google.com/maps/documentation/javascript/reference/map#MapOptions.scaleControl

        Usage::

            import gmplot
            apikey = '' # (your API key here)
            gmap = gmplot.GoogleMapPlotter(37.7670, -122.4385, 13, apikey=apikey, map_type='hybrid')
            gmap.draw("map.html")

        .. image:: GoogleMapPlotter.png

        Further customization and `styling`_::

            import gmplot

            apikey = '' # (your API key here)
            bounds = {'north': 37.967, 'south': 37.567, 'east': -122.238, 'west': -122.638}
            map_styles = [
                {
                    'featureType': 'all',
                    'stylers': [
                        {'saturation': -80},
                        {'lightness': 30},
                    ]
                }
            ]

            gmplot.GoogleMapPlotter(
                37.766956, -122.438481, 13,
                apikey=apikey,
                map_styles=map_styles,
                scale_control=True,
                fit_bounds=bounds
            ).draw("map.html")

        .. _styling: https://developers.google.com/maps/documentation/javascript/styling

        .. image:: GoogleMapPlotter_Styled.png
        '''
        # TODO: Prepend a single underscore to any attributes meant to be non-public (counts as an API change).
        self.center = (float(lat), float(lng))
        self.zoom = int(zoom)
        self.map_type = str(map_type)
        self.apikey = str(apikey)
        self.paths = []
        self.shapes = []
        self.points = []
        self.symbols = []
        self.heatmap_points = []
        self.ground_overlays = []
        self.gridsetting = None
        self.coloricon = os.path.join(os.path.dirname(__file__), 'markers/%s.png') # TODO: Unused; remove (counts as an API change).
        self.title = _get_value(kwargs, ['title'], 'Google Maps - gmplot')
        self._routes = []
        self._text_labels = []
        self._map_styles = _get_value(kwargs, ['map_styles'], [])
        self._tilt = _get_value(kwargs, ['tilt'])
        self._scale_control = _get_value(kwargs, ['scale_control'], False)
        self._fit_bounds = _get_value(kwargs, ['fit_bounds'])
        self._num_info_markers = 0
        self._marker_dropper = None

    @classmethod
    def from_geocode(cls, location, zoom=13, apikey=''):
        '''
        Initialize a GoogleMapPlotter object using a location string (instead of a specific lat/lng location).

        Requires `Geocoding API`_.

        Args:
            location (str): Location or address of interest, as a human-readable string.

        Optional:

        Args:
            zoom (int): `Zoom level`_, where 0 is fully zoomed out. Defaults to 13.
            apikey (str): Google Maps `API key`_.

        Returns:
            :class:`GoogleMapPlotter`

        .. _Geocoding API: https://console.cloud.google.com/marketplace/details/google/geocoding-backend.googleapis.com
        .. _Zoom level: https://developers.google.com/maps/documentation/javascript/tutorial#zoom-levels
        .. _API key: https://developers.google.com/maps/documentation/javascript/get-api-key

        Usage::

            import gmplot
            apikey = '' # (your API key here)
            gmap = gmplot.GoogleMapPlotter.from_geocode('Chiyoda City, Tokyo', apikey=apikey)
            gmap.draw("map.html")

        .. image:: GoogleMapPlotter.from_geocode.png
        '''
        lat, lng = cls.geocode(location, apikey=apikey)
        return cls(lat, lng, zoom, apikey=apikey)

    @classmethod
    def geocode(self, location, apikey=''): # TODO: Change to a staticmethod (counts as an API change).
        '''
        Return the lat/lng coordinates of a location string.

        Requires `Geocoding API`_.

        Args:
            location (str): Location or address of interest, as a human-readable string.

        Optional:

        Args:
            apikey (str): Google Maps `API key`_.

        .. _Geocoding API: https://console.cloud.google.com/marketplace/details/google/geocoding-backend.googleapis.com
        .. _API key: https://developers.google.com/maps/documentation/javascript/get-api-key

        Returns:
            (float, float): Latitude/longitude coordinates of the given location string.

        Usage::

            import gmplot
            apikey = '' # (your API key here)
            location = gmplot.GoogleMapPlotter.geocode('Versailles, France', apikey=apikey)
            print(location)

        .. code-block::

            -> (48.801408, 2.130122)
        '''
        geocode = requests.get(
            'https://maps.googleapis.com/maps/api/geocode/json?address="%s"&key=%s' % (location, apikey))
        geocode = json.loads(geocode.text)
        if geocode.get('error_message', ''):
            raise GoogleAPIError(geocode['error_message'])

        latlng_dict = geocode['results'][0]['geometry']['location']
        return latlng_dict['lat'], latlng_dict['lng']

    def text(self, lat, lng, text, **kwargs):
        '''
        Write a text label.

        Args:
            lat (float): Latitude of the text label.
            lng (float): Longitude of the text label.
            text (str): Text to display.

        Optional:

        Args:
            color/c (str): Text color. Can be hex ('#00FFFF'), named ('cyan'), or matplotlib-like ('c'). Defaults to black.

        Usage::

            import gmplot
            apikey = '' # (your API key here)
            gmap = gmplot.GoogleMapPlotter(37.766956, -122.438481, 13, apikey=apikey)

            gmap.text(37.793575, -122.464334, 'Presidio')
            gmap.text(37.766942, -122.441472, 'Buena Vista Park', color='blue')

            gmap.draw('map.html')

        .. image:: GoogleMapPlotter.text.png
        '''
        self._text_labels.append(_Text(lat, lng, text, **kwargs))

    def grid(self, lat_start, lat_end, lat_increment, lng_start, lng_end, lng_increment): # TODO: Replace start/end params with bounds parameter used elsewhere (counts as an API change).
        '''
        Plot a grid.

        Args:
            lat_start (float): Starting latitude of the grid.
            lat_end (float): Ending latitude of the grid.
            lat_increment (float): Distance between latitudinal divisions.
            lng_start (float): Starting longitude of the grid.
            lng_end (float): Ending longitude of the grid.
            lng_increment (float): Distance between longitudinal divisions.

        Usage::

            import gmplot
            apikey = '' # (your API key here)
            gmap = gmplot.GoogleMapPlotter(37.425, -122.145, 16, apikey=apikey)
            gmap.grid(37.42, 37.43, 0.002, -122.15, -122.14, 0.0025)
            gmap.draw('map.html')

        .. image:: GoogleMapPlotter.grid.png
        '''
        self.gridsetting = [lat_start, lat_end, lat_increment, lng_start, lng_end, lng_increment]

    def marker(self, lat, lng, color='#FF0000', c=None, title=None, precision=6, label=None, **kwargs):
        '''
        Display a marker.

        Args:
            lat (float): Latitude of the marker.
            lng (float): Longitude of the marker.

        Optional:

        Args:
            color/c (str): Marker color. Can be hex ('#00FFFF'), named ('cyan'), or matplotlib-like ('c'). Defaults to red.
            title (str): Hover-over title of the marker.
            precision (int): Number of digits after the decimal to round to for lat/lng values. Defaults to 6.
            label (str): Label displayed on the marker.
            info_window (str): HTML content to be displayed in a pop-up `info window`_.
            draggable (bool): Whether or not the marker is `draggable`_.

        .. _info window: https://developers.google.com/maps/documentation/javascript/infowindows
        .. _draggable: https://developers.google.com/maps/documentation/javascript/markers#draggable

        Usage::

            import gmplot
            apikey = '' # (your API key here)
            gmap = gmplot.GoogleMapPlotter(37.766956, -122.438481, 13, apikey=apikey)

            gmap.marker(37.793575, -122.464334, label='H', info_window="<a href='https://www.presidio.gov/'>The Presidio</a>")
            gmap.marker(37.768442, -122.441472, color='green', title='Buena Vista Park')
            gmap.marker(37.783333, -122.439494, precision=2, color='#FFD700')

            gmap.draw('map.html')

        .. image:: GoogleMapPlotter.marker.png
        '''
        self.points.append((lat, lng, c or color, title, precision, label, kwargs.get('info_window'), kwargs.get('draggable')))

    def directions(self, origin, destination, **kwargs):
        '''
        Display directions from an origin to a destination.

        Requires `Directions API`_.

        Args:
            origin ((float, float)): Origin, in latitude/longitude.
            destination ((float, float)): Destination, in latitude/longitude.

        Optional:

        Args:
            travel_mode (str): `Travel mode`_. Defaults to 'DRIVING'.
            waypoints ([(float, float)]): Waypoints to pass through.

        .. _Directions API: https://console.cloud.google.com/marketplace/details/google/directions-backend.googleapis.com
        .. _Travel mode: https://developers.google.com/maps/documentation/javascript/directions#TravelModes

        Usage::

            import gmplot
            apikey = '' # (your API key here)
            gmap = gmplot.GoogleMapPlotter(37.766956, -122.438481, 13, apikey=apikey)

            gmap.directions(
                (37.799001, -122.442692),
                (37.832183, -122.477914),
                waypoints=[
                    (37.801036, -122.434586),
                    (37.805461, -122.437262)
                ]
            )

            gmap.draw('map.html')

        .. image:: GoogleMapPlotter.directions.png
        '''
        self._routes.append(_Route(origin, destination, **kwargs))

    def scatter(self, lats, lngs, color=None, size=None, marker=True, c=None, s=None, symbol='o', **kwargs):
        '''
        Plot a collection of points.

        Args:
            lats ([float]): Latitudes.
            lngs ([float]): Longitudes.

        Optional:

        Args:
            color/c/edge_color/ec (str or [str]):
                Color of each point. Can be hex ('#00FFFF'), named ('cyan'), or matplotlib-like ('c'). Defaults to black.
            size/s (int or [int]): Size of each point, in meters (symbols only). Defaults to 40.
            marker (bool or [bool]): True to plot points as markers, False to plot them as symbols. Defaults to True.
            symbol (str or [str]): Shape of each point, as 'o', 'x', or '+' (symbols only). Defaults to 'o'.
            title (str or [str]): Hover-over title of each point (markers only).
            label (str or [str]): Label displayed on each point (markers only).
            precision (int or [int]): Number of digits after the decimal to round to for lat/lng values. Defaults to 6.
            alpha/face_alpha/fa (float or [float]):
                Opacity of each point's face, ranging from 0 to 1 (symbols only). Defaults to 0.3.
            alpha/edge_alpha/ea (float or [float]):
                Opacity of each point's edge, ranging from 0 to 1 (symbols only). Defaults to 1.0.
            edge_width/ew (int or [int]): Width of each point's edge, in pixels (symbols only). Defaults to 1.

        Usage::

            import gmplot
            apikey = '' # (your API key here)
            gmap = gmplot.GoogleMapPlotter(37.766956, -122.479481, 15, apikey=apikey)

            attractions = zip(*[
                (37.769901, -122.498331),
                (37.768645, -122.475328),
                (37.771478, -122.468677),
                (37.769867, -122.466102),
                (37.767187, -122.467496),
                (37.770104, -122.470436)
            ])

            gmap.scatter(
                *attractions,
                color=['red', 'orange', 'yellow', 'green', 'blue', 'purple'],
                s=60,
                ew=2,
                marker=[True, True, False, True, False, False],
                symbol=[None, None, 'o', None, 'x', '+'],
                title=['First', 'Second', None, 'Third', None, None],
                label=['A', 'B', 'C', 'D', 'E', 'F']
            )

            gmap.draw('map.html')

        .. image:: GoogleMapPlotter.scatter.png
        '''
        ARG_MAP = {
            'color': _ArgInfo(['color', 'c', 'edge_color', 'ec'], '#000000'),
            'size': _ArgInfo(['size', 's'], 40),
            'marker': _ArgInfo(['marker'], None),
            'symbol': _ArgInfo(['symbol'], None),
            'title': _ArgInfo(['title'], None),
            'label': _ArgInfo(['label'], None),
            'precision': _ArgInfo(['precision'], 6),
            'face_alpha': _ArgInfo(['alpha', 'face_alpha', 'fa'], 0.3),
            'edge_alpha': _ArgInfo(['alpha', 'edge_alpha', 'ea'], 1.0),
            'edge_width': _ArgInfo(['edge_width', 'ew'], 1)
        }
        # This links the draw-related settings to the arguments passed into this function.
        # Note that some settings can be set through more than one argument.
        # If no arguments are passed in for a given setting, its defined default is used.

        if len(lats) != len(lngs):
            raise ValueError("Number of latitudes and longitudes don't match!")

        # Copy the formal arguments to kwargs:
        kwargs.setdefault('color', color)
        kwargs.setdefault('c', c)
        kwargs.setdefault('size', size)
        kwargs.setdefault('s', s)
        kwargs.setdefault('marker', marker)
        kwargs.setdefault('symbol', symbol)
        # TODO: This is temporary until the function argument list is refactored to work with kwargs only.

        # For each setting...
        settings = dict()
        for setting_name, arg_info in ARG_MAP.items():

            # ...attempt to set it from kwargs (if the value isn't a list, expand it into one):
            argument_name, value = _get_value(kwargs, arg_info.arguments, arg_info.default, get_key=True)
            settings[setting_name] = value if isinstance(value, list) else [value] * len(lats)

            # ...ensure that its length matches the number of points:
            if len(settings[setting_name]) != len(lats):
                raise ValueError("`%s`'s length doesn't match the number of points!" % argument_name)

        # For each point, plot a marker or symbol with its corresponding settings:
        for i, location in enumerate(zip(lats, lngs)):
            point_settings = {setting_name: value[i] for (setting_name, value) in settings.items()}
            
            if point_settings.pop('marker'):
                self.marker(*location, **point_settings)
            else:
                self._add_symbol(Symbol(point_settings.pop('symbol'), *location, size=point_settings.pop('size')), **point_settings)

    def _add_symbol(self, symbol, **kwargs):
        '''
        Add a symbol to the list of symbols to render.

        Args:
            symbol (Symbol): Symbol to add.

        Optional:

        Args:
            edge_alpha/ea (float): Opacity of the symbol's edge, ranging from 0 to 1. Defaults to 1.0.
            edge_width/ew (int): Width of the symbol's edge, in pixels. Defaults to 1.
            face_alpha/alpha (float): Opacity of the symbol's face, ranging from 0 to 1. Defaults to 0.5.
            color/c/face_color/fc (str): Color of the symbol's face.
                Can be hex ('#00FFFF'), named ('cyan'), or matplotlib-like ('c'). Defaults to black.
            color/c/edge_color/ec (str): Color of the symbol's edge.
                Can be hex ('#00FFFF'), named ('cyan'), or matplotlib-like ('c'). Defaults to black.
        '''
        self.symbols.append((symbol, {
            'edge_alpha': _get_value(kwargs, ['edge_alpha', 'ea'], 1.0),
            'edge_width': _get_value(kwargs, ['edge_width', 'ew'], 1),
            'face_alpha': _get_value(kwargs, ['face_alpha', 'alpha'], 0.5),
            'face_color': _get_value(kwargs, ['color', 'c', 'face_color', 'fc'], '#000000'),
            'color': _get_value(kwargs, ['color', 'c', 'edge_color', 'ec'], '#000000')
        }))

    def circle(self, lat, lng, radius, color=None, c=None, alpha=0.5, **kwargs):
        '''
        Plot a circle.

        Args:
            lats (float): Latitude of the center of the circle.
            lngs (float): Longitude of the center of the circle.
            radius (int): Radius of the circle, in meters.

        Optional:

        Args:
            edge_alpha/ea (float): Opacity of the circle's edge, ranging from 0 to 1. Defaults to 1.0.
            edge_width/ew (int): Width of the circle's edge, in pixels. Defaults to 1.
            face_alpha/alpha (float): Opacity of the circle's face, ranging from 0 to 1. Defaults to 0.5.
            color/c/face_color/fc (str): Color of the circle's face.
                Can be hex ('#00FFFF'), named ('cyan'), or matplotlib-like ('c'). Defaults to black.
            color/c/edge_color/ec (str): Color of the circle's edge.
                Can be hex ('#00FFFF'), named ('cyan'), or matplotlib-like ('c'). Defaults to black.

        Usage::

            import gmplot
            apikey = '' # (your API key here)
            gmap = gmplot.GoogleMapPlotter(37.766956, -122.438481, 13, apikey=apikey)

            gmap.circle(37.776956, -122.448481, 200)
            gmap.circle(37.792915, -122.427716, 400, face_alpha=0, ew=3, color='red')
            gmap.circle(37.761601, -122.415438, 600, edge_color='#ffffff', fc='b')
            gmap.circle(37.757069, -122.457245, 800, edge_alpha=0, color='#cccccc')

            gmap.draw('map.html')

        .. image:: GoogleMapPlotter.circle.png
        '''
        self._add_symbol(Symbol('o', lat, lng, radius), color=color, c=c, alpha=alpha, **kwargs)

    def plot(self, lats, lngs, color=None, c=None, **kwargs):
        '''
        Plot a polyline.

        Args:
            lats ([float]): Latitudes.
            lngs ([float]): Longitudes.

        Optional:

        Args:
            color/c/edge_color/ec (str): Color of the polyline.
                Can be hex ('#00FFFF'), named ('cyan'), or matplotlib-like ('c'). Defaults to black.
            alpha/edge_alpha/ea (float): Opacity of the polyline, ranging from 0 to 1. Defaults to 1.0.
            edge_width/ew (int): Width of the polyline, in pixels. Defaults to 1.
            precision (int): Number of digits after the decimal to round to for lat/lng values. Defaults to 6.

        Usage::
            
            import gmplot
            apikey = '' # (your API key here)
            gmap = gmplot.GoogleMapPlotter(37.766956, -122.438481, 13, apikey=apikey)

            path = zip(*[
                (37.773097, -122.471789),
                (37.785920, -122.472693),
                (37.787815, -122.472178),
                (37.791430, -122.469763),
                (37.792547, -122.469624),
                (37.800724, -122.469460)
            ])

            gmap.plot(*path, edge_width=7, color='red')
            gmap.draw('map.html')

        .. image:: GoogleMapPlotter.plot.png
        '''
        if len(lats) != len(lngs):
            raise ValueError("Number of latitudes and longitudes don't match!")

        # Copy the formal arguments to kwargs:
        kwargs.setdefault("color", color)
        kwargs.setdefault("c", c)
        # TODO: This is temporary until the function argument list is refactored to work with kwargs only.

        self.paths.append((zip(lats, lngs), {
            'color': _get_value(kwargs, ['color', 'c', 'edge_color', 'ec'], '#000000'),
            'edge_alpha': _get_value(kwargs, ['alpha', 'edge_alpha', 'ea'], 1.0),
            'edge_width': _get_value(kwargs, ['edge_width', 'ew'], 1),
            'precision': _get_value(kwargs, ['precision'], 6)
        }))

    def heatmap(self, lats, lngs, threshold=None, radius=10, gradient=None, opacity=0.6, max_intensity=1, dissipating=True, precision=6, weights=None):
        '''
        Plot a heatmap.

        Args:
            lats ([float]): Latitudes.
            lngs ([float]): Longitudes.

        Optional:

        Args:
            threshold: (Deprecated; use `max_intensity` instead.)
            radius (int): Radius of influence for each data point, in pixels. Defaults to 10.
            gradient ([(int, int, int, float)]): Color gradient of the heatmap, as a list of `RGBA`_ colors.
                The color order defines the gradient moving towards the center of a point.
            opacity (float): Opacity of the heatmap, ranging from 0 to 1. Defaults to 0.6.
            max_intensity (int): Maximum intensity of the heatmap. Defaults to 1.
            dissipating (bool): True to dissipate the heatmap on zooming, False to disable dissipation.
            precision (int): Number of digits after the decimal to round to for lat/lng values. Defaults to 6.
            weights ([float]): List of weights corresponding to each data point. Each point has a weight
                of 1 by default. Specifying a weight of N is equivalent to plotting the same point N times.
        
        .. _RGBA: https://www.w3.org/TR/css-color-3/#rgba-color

        Usage::

            import gmplot
            apikey = '' # (your API key here)
            gmap = gmplot.GoogleMapPlotter(37.766956, -122.448481, 14, apikey=apikey)

            attractions = zip(*[
                (37.769901, -122.498331),
                (37.768645, -122.475328),
                (37.771478, -122.468677),
                (37.769867, -122.466102),
                (37.767187, -122.467496),
                (37.770104, -122.470436)
            ])

            gmap.heatmap(
                *attractions,
                radius=40,
                weights=[5, 1, 1, 1, 3, 1],
                gradient=[(0, 0, 255, 0), (0, 255, 0, 0.9), (255, 0, 0, 1)]
            )

            gmap.draw('map.html')

        .. image:: GoogleMapPlotter.heatmap.png
        '''
        # Try to give anyone using threshold a heads up.
        if threshold is not None:
            warnings.warn("The 'threshold' kwarg is deprecated, replaced in favor of 'max_intensity'.", FutureWarning)
        else:
            threshold = 10

        if len(lats) != len(lngs):
            raise ValueError("Number of latitudes and longitudes don't match!")

        if weights is None:
            weights = [self._HEATMAP_DEFAULT_WEIGHT] * len(lats)
        elif len(weights) != len(lats):
            raise ValueError("`weights`' length doesn't match the number of points!")

        self.heatmap_points.append((zip(lats, lngs, weights), {
            'threshold': threshold,
            'radius': radius,
            'gradient': gradient,
            'opacity': opacity,
            'max_intensity': max_intensity,
            'dissipating': dissipating
        }, precision))

    def ground_overlay(self, url, bounds, opacity=1.0):
        '''
        Overlay an image from a given URL onto the map.

        Args:
            url (str): URL of image to overlay.
            bounds (dict): Image bounds, as a dict of the form ``{'north':, 'south':, 'east':, 'west':}``.

        Optional:

        Args:
            opacity (float): Opacity of the overlay, ranging from 0 to 1. Defaults to 1.0.

        Usage::

            import gmplot
            apikey = '' # (your API key here)
            gmap = gmplot.GoogleMapPlotter(37.766956, -122.438481, 12, apikey=apikey)

            url = 'http://explore.museumca.org/creeks/images/TopoSFCreeks.jpg'
            bounds = {'north': 37.832285, 'south': 37.637336, 'east': -122.346922, 'west': -122.520364}
            gmap.ground_overlay(url, bounds, opacity=0.5)

            gmap.draw("map.html")

        .. image:: GoogleMapPlotter.ground_overlay.png
        '''
        self.ground_overlays.append((url, bounds, opacity))

    def polygon(self, lats, lngs, color=None, c=None, **kwargs):
        '''
        Plot a polygon.

        Args:
            lats ([float]): Latitudes.
            lngs ([float]): Longitudes.

        Optional:

        Args:
            color/c/edge_color/ec (str): Color of the polygon's edge.
                Can be hex ('#00FFFF'), named ('cyan'), or matplotlib-like ('c'). Defaults to black.
            alpha/edge_alpha/ea (float): Opacity of the polygon's edge, ranging from 0 to 1. Defaults to 1.0.
            edge_width/ew (int): Width of the polygon's edge, in pixels. Defaults to 1.
            alpha/face_alpha/fa (float): Opacity of the polygon's face, ranging from 0 to 1. Defaults to 0.3.
            color/c/face_color/fc (str): Color of the polygon's face.
                Can be hex ('#00FFFF'), named ('cyan'), or matplotlib-like ('c'). Defaults to black.
            precision (int): Number of digits after the decimal to round to for lat/lng values. Defaults to 6.

        Usage::

            import gmplot
            apikey = '' # (your API key here)
            gmap = gmplot.GoogleMapPlotter(37.766956, -122.448481, 14, apikey=apikey)

            golden_gate_park = zip(*[
                (37.771269, -122.511015),
                (37.773495, -122.464830),
                (37.774797, -122.454538),
                (37.771988, -122.454018),
                (37.773646, -122.440979),
                (37.772742, -122.440797),
                (37.771096, -122.453889),
                (37.768669, -122.453518),
                (37.766227, -122.460213),
                (37.764028, -122.510347)
            ])

            gmap.polygon(*golden_gate_park, face_color='pink', edge_color='cornflowerblue', edge_width=5)
            gmap.draw('map.html')

        .. image:: GoogleMapPlotter.polygon.png
        '''
        if len(lats) != len(lngs):
            raise ValueError("Number of latitudes and longitudes don't match!")

        # Copy the formal arguments to kwargs:
        kwargs.setdefault("color", color)
        kwargs.setdefault("c", c)
        # TODO: This is temporary until the function argument list is refactored to work with kwargs only.
        
        self.shapes.append((zip(lats, lngs), {
            'edge_color': _get_value(kwargs, ['color', 'c', 'edge_color', 'ec'], '#000000'),
            'edge_alpha': _get_value(kwargs, ['alpha', 'edge_alpha', 'ea'], 1.0),
            'edge_width': _get_value(kwargs, ['edge_width', 'ew'], 1),
            'face_alpha': _get_value(kwargs, ['alpha', 'face_alpha', 'fa'], 0.3),
            'face_color': _get_value(kwargs, ['color', 'c', 'face_color', 'fc'], '#000000'),
            'precision': _get_value(kwargs, ['precision'], 6)
        }))

    def enable_marker_dropping(self, color, **kwargs):
        '''
        Allows markers to be dropped onto the map when clicked.

        Clicking on a dropped marker will delete it.
        
        Note: Calling this function multiple times will just overwrite the existing dropped marker settings.

        Args:
            color (str): Color of the markers to be dropped.

        Optional:

        Args:
            title (str): Hover-over title of the markers to be dropped.
            label (str): Label displayed on the markers to be dropped.
            draggable (bool): Whether or not the markers to be dropped are `draggable`_.

        .. _draggable: https://developers.google.com/maps/documentation/javascript/markers#draggable

        Usage::

            import gmplot
            apikey = '' # (your API key here)
            gmap = gmplot.GoogleMapPlotter(37.766956, -122.438481, 13, apikey=apikey)
            gmap.enable_marker_dropping('orange', draggable=True)
            gmap.draw('map.html')

        .. image:: GoogleMapPlotter.enable_marker_dropping.gif
        '''
        self._marker_dropper = _MarkerDropper(color, **kwargs)

    def draw(self, file):
        '''
        Draw the HTML map to a file.

        Args:
            file (str): File to write to, as a file path.

        Usage::

            import gmplot
            apikey = '' # (your API key here)
            gmap = gmplot.GoogleMapPlotter(37.766956, -122.438481, 13, apikey=apikey)
            gmap.draw('map.html')

        .. image:: GoogleMapPlotter.draw.png
        '''
        with open(file, 'w') as f:
            with _Writer(f) as w:
                self._write_html(w)

    def get(self):
        '''
        Return the HTML map as a string.

        Returns:
            str: HTML map.

        Usage::

            import gmplot
            apikey = '' # (your API key here)
            gmap = gmplot.GoogleMapPlotter(37.766956, -122.438481, 13, apikey=apikey)
            print(gmap.get())

        .. code-block:: html
            
            -> <html>
               <head>
               <meta name="viewport" content="initial-scale=1.0, user-scalable=no" />
               <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
               <title>Google Maps - gmplot</title>
               <script type="text/javascript" src="https://maps.googleapis.com/maps/api/js?libraries=visualization"></script>
               <script type="text/javascript">
                   function initialize() {
                       var map = new google.maps.Map(document.getElementById("map_canvas"), {
                           zoom: 13,
                           center: new google.maps.LatLng(37.766956, -122.438481)
                       });

                   }
               </script>
               </head>
               <body style="margin:0px; padding:0px;" onload="initialize()">
                   <div id="map_canvas" style="width: 100%; height: 100%;" />
               </body>
               </html>
        '''
        with StringIO() as f:
            with _Writer(f) as w:
                self._write_html(w)
            return f.getvalue()

    #############################################
    # # # # # # Low level Map Drawing # # # # # #
    #############################################

    def _write_html(self, w):
        '''
        Write the HTML map.

        Args:
            w (_Writer): Writer used to write the HTML map.
        '''
        color_cache = set()

        w.write('''
            <html>
            <head>
            <meta name="viewport" content="initial-scale=1.0, user-scalable=no" />
            <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
            <title>{title}</title>
            <script type="text/javascript" src="https://maps.googleapis.com/maps/api/js?libraries=visualization{key}"></script>
            <script type="text/javascript">
        '''.format(title=self.title, key=('&key=%s' % self.apikey if self.apikey else '')))
        w.indent()
        w.write('function initialize() {')
        w.indent()
        self.write_map(w)
        self.write_grids(w)
        self.write_points(w, color_cache)
        self.write_paths(w)
        self.write_symbols(w)
        self.write_shapes(w)
        self.write_heatmap(w)
        self.write_ground_overlay(w)
        [route.write(w) for route in self._routes]
        [text.write(w) for text in self._text_labels]
        if self._marker_dropper: self._marker_dropper.write(w, color_cache)
        w.dedent()
        w.write('}')
        w.dedent()
        w.write('''
            </script>
            </head>
            <body style="margin:0px; padding:0px;" onload="initialize()">
                <div id="map_canvas" style="width: 100%; height: 100%;" />
            </body>
            </html>
        ''')

    # TODO: Prepend a single underscore to the following functions to make them non-public (counts as an API change).

    def write_grids(self, w):
        if self.gridsetting is None:
            return

        lat_start = self.gridsetting[0] # TODO: Use a better structure than a list (counts as an API change).
        lat_end = self.gridsetting[1]
        lat_increment = self.gridsetting[2]
        lng_start = self.gridsetting[3]
        lng_end = self.gridsetting[4]
        lng_increment = self.gridsetting[5]

        settings = {
            'edge_width': 1.0,
            'color': "#000000",
            'precision': 6
        }

        # Draw the grid's bounding box:
        self.write_polyline(w, [
            (lat_start, lng_start),
            (lat_end, lng_start),
            (lat_end, lng_end),
            (lat_start, lng_end),
            (lat_start, lng_start)
        ], settings)

        get_num_divisions = lambda start, end, increment: int(math.ceil((end - start) / increment))

        # Draw the grid's latitudinal divisions:
        for lat_index in range(1, get_num_divisions(lat_start, lat_end, lat_increment)):
            lat = lat_start + float(lat_index) * lat_increment
            self.write_polyline(w, [(lat, lng_start), (lat, lng_end)], settings)

        # Draw the grid's longitudinal divisions: 
        for lng_index in range(1, get_num_divisions(lng_start, lng_end, lng_increment)):
            lng = lng_start + float(lng_index) * lng_increment
            self.write_polyline(w, [(lat_start, lng), (lat_end, lng)], settings)

    def write_points(self, w, color_cache=set()):
        # TODO: Having a mutable set as a default parameter is done on purpose for backward compatibility.
        #       Should get rid of this in next major version (counts as an API change of course).
        self._num_info_markers = 0 # TODO: Instead of resetting the count here, point writing should be refactored into its own class (counts as an API change).
        for point in self.points:
            self.write_point(w, point[0], point[1], point[2], point[3], point[4], color_cache, point[5], point[6], point[7]) # TODO: Not maintainable.

    def write_circles(self, w): # TODO: Remove since unused (counts as an API change since it's technically a public function). # pragma: no coverage
        for symbol, settings in self.symbols:
            if symbol.symbol == 'o':
                self.write_symbol(w, symbol, settings)

    def write_symbols(self, w):
        for symbol, settings in self.symbols:
            self.write_symbol(w, symbol, settings)

    def write_paths(self, w):
        for path, settings in self.paths:
            self.write_polyline(w, path, settings)

    def write_shapes(self, w):
        for shape, settings in self.shapes:
            self.write_polygon(w, shape, settings)

    def write_map(self, w):
        w.write('var map = new google.maps.Map(document.getElementById("map_canvas"), {')
        w.indent()
        if self._map_styles:
            w.write('styles: %s,' % json.dumps(self._map_styles, indent=_INDENT_LEVEL))
        if self.map_type:
            w.write('mapTypeId: "%s",' % self.map_type.lower())
        if self._tilt is not None:
            w.write('tilt: %d,' % self._tilt)
        if self._scale_control:
            w.write('scaleControl: true,')
        w.write('zoom: %d,' % self.zoom)
        w.write('center: %s' % _format_LatLng(self.center[0], self.center[1]))
        w.dedent()
        w.write('});')
        w.write()
        if self._fit_bounds:
            w.write('map.fitBounds(%s);' % json.dumps(self._fit_bounds))
            w.write()

    def write_point(self, w, lat, lng, color, title, precision, color_cache, label, info_window=None, draggable=None): # TODO: Bundle args into some Point or Marker class (counts as an API change).
        # Write the marker icon (if it isn't written already).
        marker_icon = _MarkerIcon(color)
        marker_icon.write(w, color_cache)

        # If this marker should have an info window, give it a unique name:
        marker_name = ('info_marker_%d' % self._num_info_markers) if info_window is not None else None

        # Write the actual marker:
        marker = _Marker(_format_LatLng(lat, lng, precision), name=marker_name, title=title, label=label, icon=marker_icon.name, draggable=draggable)
        marker.write(w)

        # Write the marker's info window, if specified:
        if info_window is not None:
            marker_info_window = _MarkerInfoWindow(marker_name, info_window)
            marker_info_window.write(w, self._num_info_markers)
            self._num_info_markers += 1

        # TODO: When Point-writing is pulled into its own class, move _MarkerIcon, _Marker, and _MarkerInfoWindow initialization into _Point's constructor.

    def write_symbol(self, w, symbol, settings):
        try:
            template = SYMBOLS[symbol.symbol]
        except KeyError:
            raise InvalidSymbolError("Symbol %s is not implemented" % symbol.symbol)

        w.write(template.format(
            lat=symbol.lat,
            long=symbol.long,
            size=symbol.size,
            strokeColor=_get_hex_color(settings.get('color')),
            strokeOpacity=settings.get('edge_alpha'),
            strokeWeight=settings.get('edge_width'),
            fillColor=_get_hex_color(settings.get('face_color')),
            fillOpacity=settings.get('face_alpha')
        ))
        w.write()

    def write_circle(self, w, lat, long, size, settings): # TODO: Remove since unused (counts as an API change since it's technically a public function). # pragma: no coverage
        self.write_symbol(w, Symbol('o', lat, long, size), settings)

    def write_polyline(self, w, path, settings):
        w.write('new google.maps.Polyline({')
        w.indent()
        w.write('clickable: %s,' % str(False).lower())
        w.write('geodesic: %s,' % str(True).lower())
        w.write('strokeColor: "%s",' % _get_hex_color(settings.get('color')))
        if settings.get('edge_alpha', None) is not None:
            w.write('strokeOpacity: %f,' % settings['edge_alpha'])
        w.write('strokeWeight: %d,' % settings.get('edge_width'))
        w.write('map: map,')
        w.write('path: [')
        w.indent()
        for coordinate in path:
            w.write('%s,' % _format_LatLng(coordinate[0], coordinate[1], settings.get("precision")))
        w.dedent()
        w.write(']')
        w.dedent()
        w.write('});')
        w.write()

    def write_polygon(self, w, path, settings):
        w.write('new google.maps.Polygon({')
        w.indent()
        w.write('clickable: %s,' % str(False).lower())
        w.write('geodesic: %s,' % str(True).lower())
        w.write('fillColor: "%s",' % _get_hex_color(settings.get('face_color')))
        w.write('fillOpacity: %f,' % settings.get('face_alpha'))
        w.write('strokeColor: "%s",' % _get_hex_color(settings.get('edge_color')))
        w.write('strokeOpacity: %f,' % settings.get('edge_alpha'))
        w.write('strokeWeight: %d,' % settings.get('edge_width'))
        w.write('map: map,')
        w.write('paths: [')
        w.indent()
        for coordinate in path:
            w.write('%s,' % _format_LatLng(coordinate[0], coordinate[1], settings.get("precision")))
        w.dedent()
        w.write(']')
        w.dedent()
        w.write('});')
        w.write()

    def write_heatmap(self, w):
        for heatmap_points, settings_dict, precision in self.heatmap_points:
            w.write('new google.maps.visualization.HeatmapLayer({')
            w.indent()
            w.write('threshold: %d,' % settings_dict['threshold'])
            w.write('radius: %d,' % settings_dict['radius'])
            w.write('maxIntensity: %d,' % settings_dict['max_intensity'])
            w.write('opacity: %f,' % settings_dict['opacity'])
            w.write('dissipating: %s,' % ('true' if settings_dict['dissipating'] else 'false'))
            if settings_dict['gradient']:
                w.write('gradient: [')
                w.indent()
                for r, g, b, a in settings_dict['gradient']:
                    w.write('"rgba(%d, %d, %d, %f)",' % (r, g, b, a))
                w.dedent()
                w.write('],')
            w.write('map: map,')
            w.write('data: [')
            w.indent()
            for lat, lng, weight in heatmap_points:
                location = _format_LatLng(lat, lng, precision)
                if weight == self._HEATMAP_DEFAULT_WEIGHT:
                    w.write('%s,' % location)
                else:
                    w.write('{location: %s, weight: %f},' % (location, weight)) 
            w.dedent()
            w.write(']')
            w.dedent()
            w.write('});')
            w.write()

    def write_ground_overlay(self, w):
        for url, bounds, opacity in self.ground_overlays:
            w.write('''
                new google.maps.GroundOverlay(
                    "{url}",
                    {bounds},
                    {{
                        opacity: {opacity},
                        map: map,
                        clickable: false
                    }}
                );
            '''.format(url=url, bounds=json.dumps(bounds), opacity=opacity))
            w.write()

if __name__ == "__main__": # pragma: no coverage
    apikey=''

    mymap = GoogleMapPlotter(37.428, -122.145, 16, apikey)
    # mymap = GoogleMapPlotter.from_geocode("Stanford University", apikey)

    mymap.grid(37.42, 37.43, 0.001, -122.15, -122.14, 0.001)
    mymap.marker(37.427, -122.145, "yellow")
    mymap.marker(37.428, -122.146, "cornflowerblue")
    mymap.marker(37.429, -122.144, "k")
    lat, lng = mymap.geocode("Stanford University", apikey)
    mymap.marker(lat, lng, "red", info_window="<a href='https://www.stanford.edu/'>Stanford University</a>")
    mymap.circle(37.429, -122.145, 100, "#FF0000", ew=2)
    path = [(37.429, 37.428, 37.427, 37.427, 37.427),
             (-122.145, -122.145, -122.145, -122.146, -122.146)]
    path2 = [[i+.01 for i in path[0]], [i+.02 for i in path[1]]]
    path3 = [(37.433302 , 37.431257 , 37.427644 , 37.430303), (-122.14488, -122.133121, -122.137799, -122.148743)]
    path4 = [(37.423074, 37.422700, 37.422410, 37.422188, 37.422274, 37.422495, 37.422962, 37.423552, 37.424387, 37.425920, 37.425937),
         (-122.150288, -122.149794, -122.148936, -122.148142, -122.146747, -122.14561, -122.144773, -122.143936, -122.142992, -122.147863, -122.145953)]
    mymap.plot(path[0], path[1], "plum", edge_width=10)
    mymap.plot(path2[0], path2[1], "red")
    mymap.polygon(path3[0], path3[1], edge_color="cyan", edge_width=5, face_color="blue", face_alpha=0.1)
    mymap.heatmap(path4[0], path4[1], threshold=10, radius=40)
    mymap.heatmap(path3[0], path3[1], threshold=10, radius=40, dissipating=False, gradient=[(30,30,30,0), (30,30,30,1), (50, 50, 50, 1)])
    mymap.scatter(path4[0], path4[1], c='r', marker=True)
    mymap.scatter(path4[0], path4[1], s=90, marker=False, alpha=0.9, symbol='x', c='red', edge_width=4)
    # Get more points with:
    # http://www.findlatitudeandlongitude.com/click-lat-lng-list/
    scatter_path = ([37.424435, 37.424417, 37.424417, 37.424554, 37.424775, 37.425099, 37.425235, 37.425082, 37.424656, 37.423957, 37.422952, 37.421759, 37.420447, 37.419135, 37.417822, 37.417209],
                    [-122.142048, -122.141275, -122.140503, -122.139688, -122.138872, -122.138078, -122.137241, -122.136405, -122.135568, -122.134731, -122.133894, -122.133057, -122.13222, -122.131383, -122.130557, -122.129999])
    mymap.scatter(scatter_path[0], scatter_path[1], c='r', marker=True)
    mymap.draw('./mymap.html')
