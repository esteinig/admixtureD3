from glob import glob
import os
from admix.core import MetaData, AdmixtureD3
from admix.utils import stamp, CommandLine


def main():

    stamp("Welcome to Admixture D3.")
    stamp("Parsing command line arguments...")

    cmd = CommandLine()

    args = vars(cmd.args)

    stamp("Parsing admixture files...")
    q_files = [os.path.abspath(file) for arg in args["admixture"] for file in glob(arg)]
    q_files = list(set(q_files))

    stamp("Parsing meta data...")
    md = MetaData(file=args["meta"], sep=",")

    if args["wiki"]:
        if "wiki" in md.meta.columns:
            stamp("Detected column for Wikipedia.")
            md.get_wikipedia(column="wiki")
        else:
            stamp("Could not find column for Wikipedia. Exiting...")
            exit(1)

    if args["geo"]:
        if "geo" in md.meta.columns:
            stamp("Detected column for geographical information.")
            md.get_locations(column="geo")
        else:
            stamp("Could not find column for geographical information. Exiting...")
            exit(1)
    
    adm = AdmixtureD3(project=args["project"], qfiles=q_files, meta=md.meta, config=args["config"])

    adm.write_project(wiki=md.wiki_data, geo=md.geo_data)

main()