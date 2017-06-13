import os
import time
import argparse
import textwrap

from numpy import nan

# Time Stamp for STDOUT

def stamp(*args):

    print(str(time.strftime("[%H:%M:%S]")) + " " + " ".join([str(arg) for arg in args]))

# Decorators


def wikihtml(func):

    """
    Decorator for _get_wikipedia_summary(search_string), which takes one positional argument 'search_string' and
    return string tuple (title, summary) which is then decorated as HTML:

    """

    def wrapper(*args):

        title, summary, url = func(*args)

        if title is nan:
            title = ""

        if summary is nan:
            summary = "No summary available on Wikipedia."

        html = textwrap.dedent("""
        <br>
        <p>
        {summary}
        </p>
        <br>
        """.format(summary=summary))

        return {"title": title, "text": html, "url": url}

    return wrapper


class CommandLine:

    def __init__(self):

        parser = argparse.ArgumentParser(description='Command line interface for Admixture D3')

        parser.add_argument('-m', '--meta', type=lambda p: os.path.abspath(p), default="meta.csv")
        parser.add_argument('-q', '--admixture', nargs="*")

        parser.add_argument('-p', '--project', type=str, default="AdmixtureD3")
        parser.add_argument('-o', '--outdir', type=lambda p: os.path.abspath(p), default=os.getcwd())

        parser.add_argument('--palette', type=str, default="Dark2")
        parser.add_argument('--colours', type=lambda c: [str(item) for item in c.split(",")], default=None)

        parser.add_argument('--geo', action="store_true", default=False)
        parser.add_argument('--wiki', action="store_true", default=False)

        parser.add_argument('--config', type=lambda p: os.path.abspath(p), default=None)

        self.args = parser.parse_args(["-m", "test/meta.csv", "-q",  "./test/*.Q", "--palette", "Pastel1"   ,
                                       "--geo"])
