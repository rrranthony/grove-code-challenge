import argparse
import csv
import json
import math
import sys
from typing import List, NamedTuple

import geocoder


KM_TO_MI = 0.621371
EARTH_RADIUS_KM = 6371
EARTH_RADIUS_MI = EARTH_RADIUS_KM * KM_TO_MI


class GeocodingError(Exception):
    """Generic exception denoting any error encountered during geocoding."""
    pass


class Point(NamedTuple):
    latitude: float  # degrees
    longitude: float  # degrees

    @property
    def latitude_radians(self):
        return math.radians(self.latitude)

    @property
    def longitude_radians(self):
        return math.radians(self.longitude)


class Store(NamedTuple):
    name: str
    location: str
    address: str
    city: str
    state: str
    zip_code: str
    latitude: float
    longitude: float
    county: str
    distance_to_store: float

    def __format__(self, format_spec: str) -> str:
        if format_spec == 'json':
            output_dict = self._asdict()
            if self.distance_to_store is None:
                del output_dict['distance_to_store']
            return json.dumps(output_dict)
        elif format_spec == 'text':
            output = f'{self.address}, {self.city}, {self.state}, {self.zip_code}'
            if self.distance_to_store is not None:
                output = f'{output}\nDistance to store: {self.distance_to_store:.2f}'
            return output
        elif format_spec == '':
            return str(self)
        else:
            raise ValueError('Invalid format specifier. Valid format specifiers: [json, text]')

    def __str__(self) -> str:
        return f'{self.name} located at {self.address}, {self.city}, {self.state}, {self.zip_code}'


def parse_args() -> argparse.Namespace:
    description = ('Locate the nearest store (as the crow flies) from store-locations.csv. Print the store address as '
                   'well as the distance to the store.')
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        '--address',
        type=str,
        help='Find nearest store to this address. If there are multiple best-matches, return the first.'
    )
    parser.add_argument(
        '--zip',
        dest='zip_code',
        type=str,
        help='Find nearest store to this zip code. If there are multiple best-matches, return the first.'
    )
    parser.add_argument(
        '--units',
        choices=['mi', 'km'],
        default='mi',
        type=str,
        help='Display units in miles or kilometers [default: mi]'
    )
    parser.add_argument(
        '--output',
        dest='output_format',
        choices=['text', 'json'],
        default='text',
        type=str,
        help='Output in human-readable text, or in JSON (e.g. machine-readable) [default: text]'
    )
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()
    if not args.address and not args.zip_code:
        parser.error('Must specify address or zip')
    if args.address and args.zip_code:
        parser.error('Only one of address or zip is allowed')
    return args


def load_stores(has_header_row: bool = True) -> List[Store]:
    csv_filename = 'store-locations.csv'
    stores = []
    with open(csv_filename) as csv_file:
        csv_reader = csv.reader(csv_file)
        if has_header_row:
            next(csv_reader)
        for row in csv_reader:
            row[6] = float(row[6])  # convert latitude to float
            row[7] = float(row[7])  # convert longitude to float
            # Hack: since we're using a namedtuple, where it's not really straightforward to set defaults for a field,
            # we manually default `distance_to_store` here.
            distance_to_store = None
            row.append(distance_to_store)
            store = Store._make(row)
            stores.append(store)
    return stores


def geocode(search_location: str) -> Point:
    try:
        geocoded_location = geocoder.osm(search_location)
    except Exception as e:
        raise GeocodingError(e)

    if not geocoded_location.ok:
        raise(GeocodingError(f'No result found for {search_location}'))
    latitude, longitude = geocoded_location.latlng[:]
    return Point(latitude, longitude)


def distance_between(point_a: Point, point_b: Point, units: str = 'mi') -> float:
    # Use the haversine formula: https://en.wikipedia.org/wiki/Haversine_formula#The_haversine_formula
    if units == 'mi':
        sphere_radius = EARTH_RADIUS_MI
    else:
        sphere_radius = EARTH_RADIUS_KM
    sqrt_arg1 = math.sin((point_b.latitude_radians - point_a.latitude_radians) / 2)**2
    sqrt_arg2 = (math.cos(point_a.latitude_radians)
                 * math.cos(point_b.latitude_radians)
                 * math.sin((point_b.longitude_radians - point_a.longitude_radians) / 2)**2)
    arcsin_arg = math.sqrt(sqrt_arg1 + sqrt_arg2)
    distance = (2 * sphere_radius * math.asin(arcsin_arg))
    return distance


def find_nearest_store(search_point: Point, stores: List[Store], units: str = 'mi') -> Store:
    if units == 'mi':
        earth_circumference = 2 * math.pi * EARTH_RADIUS_MI
    else:
        earth_circumference = 2 * math.pi * EARTH_RADIUS_KM
    smallest_distance = earth_circumference
    for store in stores:
        store_point = Point(store.latitude, store.longitude)
        distance_to_store = distance_between(search_point, store_point, units=units)
        if distance_to_store < smallest_distance:
            nearest_store = store._replace(distance_to_store=distance_to_store)
            smallest_distance = distance_to_store
    return nearest_store


def main():
    args = parse_args()
    stores = load_stores()
    search_location = args.address or args.zip_code
    try:
        geocoded_search_point = geocode(search_location)
    except GeocodingError as e:
        sys.exit(e)
    nearest_store = find_nearest_store(geocoded_search_point, stores, args.units)
    print(f'{nearest_store:{args.output_format}}')


if __name__ == '__main__':
    main()
