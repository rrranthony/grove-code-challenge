from unittest.mock import ANY, Mock, call, patch

import pytest

from store_finder.store_finder import (
    GeocodingError,
    Point,
    Store,
    parse_args,
    geocode,
    distance_between,
    find_nearest_store
)


@pytest.fixture
def store_without_distance():
    return Store(
        name='Crystal',
        location='SWC Broadway & Bass Lake Rd',
        address='5537 W Broadway Ave',
        city='Crystal',
        state='MN',
        zip_code='55428-3507',
        latitude=45.0521539,
        longitude=-93.364854,
        county='Hennepin County',
        distance_to_store=None
    )


@pytest.fixture
def store_with_distance(store_without_distance):
    return store_without_distance._replace(distance_to_store=1.0)


def test__store__json_output(store_without_distance, store_with_distance):
    expected_store_without_distance_json = (
        '{"name": "Crystal", "location": "SWC Broadway & Bass Lake Rd", "address": "5537 W Broadway Ave", '
        '"city": "Crystal", "state": "MN", "zip_code": "55428-3507", "latitude": 45.0521539, "longitude": -93.364854, '
        '"county": "Hennepin County"}'
    )
    expected_store_with_distance_json = (
        '{"name": "Crystal", "location": "SWC Broadway & Bass Lake Rd", "address": "5537 W Broadway Ave", '
        '"city": "Crystal", "state": "MN", "zip_code": "55428-3507", "latitude": 45.0521539, "longitude": -93.364854, '
        '"county": "Hennepin County", "distance_to_store": 1.0}'
    )

    assert f'{store_without_distance:json}' == expected_store_without_distance_json
    assert f'{store_with_distance:json}' == expected_store_with_distance_json


def test__store__text_output(store_without_distance, store_with_distance):
    expected_store_without_distance_text = '5537 W Broadway Ave, Crystal, MN, 55428-3507'
    expected_store_with_distance_text = '5537 W Broadway Ave, Crystal, MN, 55428-3507\nDistance to store: 1.00'

    assert f'{store_without_distance:text}' == expected_store_without_distance_text
    assert f'{store_with_distance:text}' == expected_store_with_distance_text


def test__store__output_no_format_spec(store_without_distance, store_with_distance):
    expected_output = 'Crystal located at 5537 W Broadway Ave, Crystal, MN, 55428-3507'

    assert f'{store_without_distance}' == expected_output
    assert f'{store_with_distance}' == expected_output


def test__store__invalid_format_spec(store_without_distance):
    with pytest.raises(ValueError):
        f'{store_without_distance:invalid_format_spec}'


def test__store__str(store_without_distance, store_with_distance):
    expected_output = 'Crystal located at 5537 W Broadway Ave, Crystal, MN, 55428-3507'

    assert str(store_without_distance) == expected_output
    assert str(store_with_distance) == expected_output


@patch('store_finder.store_finder.argparse')
def test__parse_args(mock_argparse):
    mock_args = Mock()
    mock_parser = Mock()
    mock_parser.parse_args.return_value = mock_args
    mock_argparse.ArgumentParser.return_value = mock_parser

    expected_parser_add_argument_calls = [
        call('--address', type=str, help=ANY),
        call('--zip', dest=ANY, type=str, help=ANY),
        call('--units', choices=['mi', 'km'], default='mi', type=str, help=ANY),
        call('--output', dest=ANY, choices=['text', 'json'], default='text', type=str, help=ANY)
    ]
    expected_args = mock_args

    args = parse_args()

    mock_argparse.ArgumentParser.assert_called_once()
    mock_parser.add_argument.assert_has_calls(expected_parser_add_argument_calls)
    assert args == expected_args


@patch('store_finder.store_finder.sys')
@patch('store_finder.store_finder.argparse')
def test__parse_args__no_args(mock_argparse, mock_sys):
    mock_parser = Mock()
    mock_argparse.ArgumentParser.return_value = mock_parser
    mock_sys.argv = ['prog']

    parse_args()

    mock_parser.print_help.assert_called_once_with()
    mock_sys.exit.assert_called_once_with(1)


@patch('store_finder.store_finder.argparse')
def test__parse_args__invalid_args(mock_argparse):
    mock_args = Mock()
    mock_args.address = None
    mock_args.zip_code = None
    mock_parser = Mock()
    mock_parser.parse_args.return_value = mock_args
    mock_argparse.ArgumentParser.return_value = mock_parser

    # Both address and zip missing
    parse_args()

    mock_parser.error.assert_called_once_with('Must specify address or zip')

    # Both address and zip specified
    mock_parser.reset_mock()
    mock_args.address = '1462 Pine St, San Francisco, CA 94109'
    mock_args.zip_code = '94109'

    parse_args()

    mock_parser.error.assert_called_once_with('Only one of address or zip is allowed')


@patch('store_finder.store_finder.Point')
@patch('store_finder.store_finder.geocoder')
def test__geocode(mock_geocoder, mock_point):
    search_location = '1462 Pine St, San Francisco, CA 94109'
    mock_geocoded_location = Mock()
    mock_geocoded_location.ok = True
    mock_geocoded_location.latlng = [37.789783, -122.419862]
    mock_geocoder.osm.return_value = mock_geocoded_location
    expected_geocoded_location = mock_point(37.789783, -122.419862)

    geocoded_location = geocode(search_location)

    mock_geocoder.osm.assert_called_once_with(search_location)
    assert geocoded_location == expected_geocoded_location


@patch('store_finder.store_finder.geocoder')
def test__geocode__exception(mock_geocoder):
    search_location = '1462 Pine St, San Francisco, CA 94109'
    mock_geocoder.osm.side_effect = Exception()

    with pytest.raises(GeocodingError):
        geocode(search_location)


@patch('store_finder.store_finder.geocoder')
def test__geocode__no_result(mock_geocoder):
    search_location = '1462 Pine St, San Francisco, CA 94109'
    mock_geocoded_location = Mock()
    mock_geocoded_location.ok = False
    mock_geocoder.osm.return_value = mock_geocoded_location

    with pytest.raises(GeocodingError):
        geocode(search_location)


def test__distance_between():
    point_a = Point(latitude=133, longitude=37)
    point_b = Point(latitude=133.608, longitude=37)

    distance_mi = distance_between(point_a, point_b, units='mi')
    distance_km = distance_between(point_a, point_b, units='km')

    assert distance_mi == pytest.approx(42, rel=0.01)
    assert distance_km == pytest.approx(67.6, rel=0.01)


@patch('store_finder.store_finder.distance_between')
@patch('store_finder.store_finder.Point')
def test__find_nearest_store(mock_point, mock_distance_between):
    search_point = Mock()
    mock_distance_between.side_effect = [2.0, 1.0, 3.0]
    mock_store_1 = Mock()
    mock_store_2 = Mock()
    mock_store_3 = Mock()
    stores = [mock_store_1, mock_store_2, mock_store_3]

    nearest_store = find_nearest_store(search_point, stores)

    assert mock_point.call_count == len(stores)
    assert mock_distance_between.call_count == len(stores)
    mock_store_1._replace.assert_called_once_with(distance_to_store=2.0)
    mock_store_2._replace.assert_called_once_with(distance_to_store=1.0)
    mock_store_3._replace.assert_not_called
    assert nearest_store == mock_store_2._replace.return_value
