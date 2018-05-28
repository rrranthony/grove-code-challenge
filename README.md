# Find Store
This is my solution to the Grove Collaborative [find store coding challenge](https://github.com/groveco/code-challenge).

The approach this solution uses is as follows:
1. Parse command-line arguments
1. Load store location data from the `store-locations.csv` file
1. Geocode the search location (either an address or a zip code) to obtain the latitude and longitude coordinates we 
are trying to find the closest store to
1. Calculate the distance from the search latitude and longitude to each store (using the
[haversine formula](https://en.wikipedia.org/wiki/Haversine_formula#The_haversine_formula)), keeping track of the nearest 
store and its distance
1. Print out the matching store address, as well as the distance to the store


# Requirements
The requirements for the `find_store` command-line tool are:
* Bash
* Python 3.6.5 (any Python 3.6.x should work), with executable `python3` available


# Setup
To get set up to use `find_store`:
1. Clone this repository
1. Change to the root directory of the cloned repository
1. Run the `setup` script using

    ```bash
    ./script/setup
    ```

The `setup` script should output the following:

```
Setting up find_store Python virtual environment
Creating find_store Python virtual environment...done.
Installing requirements into find_store Python virtual environment...done.
find_store Python virtual environment setup complete.
```

Once the `setup` script has completed, you are ready to use `find_store`.


# Usage
The usage for `find_store` is as follows:

```
$ ./find_store --help
usage: store_finder.py [-h] [--address ADDRESS] [--zip ZIP_CODE]
                       [--units {mi,km}] [--output {text,json}]

Locate the nearest store (as the crow flies) from store-locations.csv. Print
the store address as well as the distance to the store.

optional arguments:
  -h, --help            show this help message and exit
  --address ADDRESS     Find nearest store to this address. If there are
                        multiple best-matches, return the first.
  --zip ZIP_CODE        Find nearest store to this zip code. If there are
                        multiple best-matches, return the first.
  --units {mi,km}       Display units in miles or kilometers [default: mi]
  --output {text,json}  Output in human-readable text, or in JSON (e.g.
                        machine-readable) [default: text]
```


# Examples
```
$ ./find_store --address="1462 Pine St, San Francisco, CA 94109"
789 Mission St, San Francisco, CA, 94103-3132
Distance to store: 0.95
```
```
$ ./find_store --address="1462 Pine St, San Francisco, CA 94109" --units=km
789 Mission St, San Francisco, CA, 94103-3132
Distance to store: 1.53
```
```
$ ./find_store --address="1462 Pine St, San Francisco, CA 94109" --units=km --output=json
{"name": "San Francisco Central", "location": "SEC 4th & Mission St", "address": "789 Mission St", "city": "San Francisco", "state": "CA", "zip_code": "94103-3132", "latitude": 37.7847358, "longitude": -122.4036914, "county": "San Francisco County", "distance_to_store": 1.5279124666040573}
``` 


# Running Tests
Use the same steps to get set up to use `find_store`, but instead of running `./script/setup`, run

```bash
./script/setup test
```

The `setup` script should output the following:

```
Setting up find_store test Python virtual environment
Creating find_store test Python virtual environment...done.
Installing requirements into find_store test Python virtual environment...done.
find_store test Python virtual environment setup complete.
```

Tests can then be run using

```bash
./script/test
```

Example:

```
$ ./script/test
Running pyflakes...
Running pycodestyle...
Running pytest...
.............                                                                                                           [100%]

---------- coverage: platform darwin, python 3.6.5-final-0 -----------
Name                           Stmts   Miss  Cover   Missing
------------------------------------------------------------
store_finder/store_finder.py     117     24    79%   108-123, 157, 169-177

13 passed in 0.41 seconds
```