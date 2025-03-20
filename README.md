Data availability tools for miniSEED archives
=============================================
A small utility package that can be used to compute data availability for various datastreams stored in a miniSEED archive.

Installation
------------
Clone this GitHub:

```console
git clone https://github.com/AVERT-System/miniseed-availability
cd miniseed-availability
```

We recommend using ``uv``, a fast Python package and project manager, to create a virtual environment in which to isolate the package.

```console
uv venv --python=3.12
source .venv/bin/activate
uv pip install
```

Usage
-----
Once installed, the package is straightforward to use. First, make a copy of the example config file, stored in ``config/example.toml``, and adjust the fields for your local archive. The example is reproduced below:

```console
[compute]
stations = [
    "NW.STAT1",
    "NW.STAT2",
    "NW.STAT3",
]
years = [
    2020,
    2021,
    2022,
    2023,
    2024,
    2025
]
channel = "*HZ"
archive_path = "/data/archive/miniseed"
product_path = "/data/products"

[visualise]
starttime = "2020-02-18"
endtime = "2025-02-18"
stations = [
    "NW.STAT1",
    "NW.STAT2",
    "NW.STAT3",
]
channel = "*HZ"
product_path = "/data/products"
filename = "example-availability-plot"

```

Once done, you can run the compute portion of the toolkit as:

```console
mseed-availability compute --config <path/to/config.toml>
```

This will run through the archive by year, then by station, writing the computed availability to a .csv file in the designated products archive.

You can then create simple visualisations of these computed availabilities using:

```console
mseed-availability visualise --config <path/to/config.toml>
```

This will read in the previously computed availability CSV files for each station between the specified start- and endtimes, and plot them as a bar chart.

Contact
-------
Any comments/questions can be directed to:
* **Conor Bacon** - cbacon [ at ] ldeo.columbia.edu

License
-------
This simple tool is shared here "as is", with no license. Do with it what you will.
