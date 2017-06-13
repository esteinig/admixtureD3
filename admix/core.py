import pandas
import wikipedia
import os
import shutil
from wikipedia import PageError, RedirectError, HTTPTimeoutError, DisambiguationError
import json

import re
from numpy import nan
from pycountry import countries
from pygeocoder import Geocoder, GeocoderError

from admix.utils import wikihtml, stamp


class AdmixtureD3:

    def __init__(self, qfiles, meta, project ="AdmixtureD3", palette="Dark2", colours=None, config=None,
                 outdir=os.getcwd(), force=True):

        self.project = project
        self.outdir = outdir
        self.force = force

        self.meta = meta
        self.config = config

        self.palette = palette
        self.colours = colours

        self.bar_height = 256
        self.bar_width = 16

        self.option_align = "center"

        self.qfiles = qfiles

        self._setup_project()
        self._get_q_data()

        self.data = dict()

        self.wiki_data = dict()
        self.geo_data = dict()

        self.project_files = {
            "css": [
                self._get_basefile("main.css")
            ],
            "js": [
                self._get_basefile("helper.js"),
                self._get_basefile("main.js")
            ]
        }

    def _get_basefile(self, file):

        return os.path.join(os.path.dirname(os.path.abspath(__file__)), file)

    def _setup_project(self):

        os.makedirs(self.outdir, exist_ok=True)

        os.makedirs(self.outdir)
        for sub_dir in ("css", "js"):
            os.makedirs(sub_dir)

    def _get_q_data(self):

        self.q_values = {}
        self.k_values = []
        for file in self.qfiles:
            k = self._get_k_from_filename(os.path.basename(file))
            q_df = pandas.read_csv(file, sep=" ", header=None)
            q_df.columns = [str(i) for i in range(1, len(q_df.columns)+1)]
            q_df.index = self.meta["id"].tolist()

            # Dictionary (key: K, value: dict of
            # keys: ID value: list of values at K)
            self.q_values[k] = q_df.T.to_dict(orient="list")
            self.k_values.append(k)

        self.k_values.sort(key=int)

    def _transform(self):

        """ Main function for transforming into template JSON data entry: """

        data = {
            "samples": [],
            "config": {
                "pops": len(self.meta["pop"].unique()),
                "n": len(self.meta),
                "palette": "Dark2",
                "colours": self.colours,
                "bar_width": self.bar_width,
                "bar_height": self.bar_height,
                "K": self.k_values,
                "option_align": self.option_align
                }
            }

        for i, entry in self.meta.iterrow():

            sample = {
                "id": entry["id"],
                "image": entry["image"],
                "info": {
                    "title": entry["title"],
                    "text": entry["text"],
                    "url": None
                },
                "geo": None,
                "pop": entry["pop"],
                "K": {K: self.q_values[K] for K in self.k_values}

            }

            data["samples"].append(sample)

        self.data = data

        return data

    def _get_k_from_filename(self, name):

        """ Gert trailing K value from string of Q file name, e.g. admixture.8.Q """

        name, ext = os.path.splitext(name)

        return self._get_trailing_number(name)

    @staticmethod
    def _get_trailing_number(s):

        """ Get trailing number from string. """

        m = re.search(r'\d+$', s)
        return int(m.group()) if m else None

    def write_project(self, wiki=None, geo=None):

        # Generates data for Admixture D3

        if wiki is None:
            for sample in self.data["samples"]:
                sample["info"] = wiki[sample["id"]]

        if geo is not None:
            # add geographic data here
            for sample in self.data["samples"]:
                sample["info"] = geo[sample["id"]]

        file_path = os.path.join(self.outdir, "data.json")

        with open(file_path, "w") as data_file:
            json.dumps(data_file)

        for target_dir, files in self.project_files.items():
            for file in files:
                shutil.copy(target_dir, file)

        shutil.copy(self._get_basefile("main.html"),
                    os.path.join(self.outdir, self.project + "html"))
        

class MetaData:

    def __init__(self, file, sep=","):

        self.file = file

        self.meta = pandas.read_csv(file, sep=sep)

        self.meta.columns = [col.lower() for col in self.meta.columns]

        self.geo_df = None
        self.wiki_df = None

        # Wikipedia dictionary of Title, Text and URL for Admixture D3
        self.wiki = None

    def get_locations(self, column):

        geo = {field: self._get_geo_row(field) for field in self.meta[column].unique()}
        self.geo_data = {self.meta.loc[i, "ID"]: self.wiki[entry] for i, entry in enumerate(self.meta[column])}
        self.geo_df = pandas.DataFrame([geo[entry] for entry in self.meta[column]],
                                        columns=["Country", "City", "ISO3", "Latitude", "Longitude"])

    def get_wikipedia(self, column):

        wiki = {field: self._get_wikipedia_summary(field) for field in self.meta[column].unique()}
        self.wiki_data = {self.meta.loc[i, "ID"]: wiki[entry] for i, entry in enumerate(self.meta[column])}

        self.wiki_df = pandas.DataFrame([self.wiki[entry]["text"] for entry in self.meta[column]])

    @wikihtml
    def _get_wikipedia_summary(self, search_string):

        try:
            summary = wikipedia.summary(search_string)
            page = wikipedia.page(search_string)
            title = page.title
            url = page.url

            return title, summary, url

        except (PageError, RedirectError):
            print("Could not find Wikipedia entry for:", search_string)
            return nan, nan, nan
        except HTTPTimeoutError:
            print("Could not reach Wikipedia")
            return nan, nan, nan
        except DisambiguationError:
            print("Disambigous search results for:", search_string)
            return nan, nan, nan

    @staticmethod
    def _get_geo_row(geo_string, clean=None):

        entry = {"Country": nan, "City": nan, "ISO3": nan, "Latitude": nan, "Longitude": nan}

        if geo_string is nan:
            return entry

        if clean is not None:
            for term in clean:
                geo_string = geo_string.replace(term, "")

        gc = Geocoder()

        try:
            results = gc.geocode(geo_string)
        except GeocoderError:
            return entry

        try:
            geo_country = countries.get(name=results.country)
        except KeyError:
            try:
                geo_country = countries.get(official_name=results.country)
            except KeyError:
                return entry

        iso = geo_country.alpha_3
        name = geo_country.name
        lat = float(results.latitude)
        lon = float(results.longitude)

        if results.city is None:
            city = nan
        else:
            city = results.city

        return {"Country": name, "City": city, "ISO3": iso, "Latitude": lat, "Longitude": lon}
