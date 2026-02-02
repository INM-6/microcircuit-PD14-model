import sys
from pathlib import Path

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# Import pybtex modules at top level  # noqa: E402
from pybtex.style.formatting.unsrt import Style as UnsrtStyle  # noqa: E402
from pybtex.style.sorting import BaseSortingStyle  # noqa: E402

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'PD14'
copyright = '2025, nest-devs'
author = 'nest-devs'

sys.path.insert(0, str(Path('..', 'PyNEST/src').resolve()))

# -- Run publication processing scripts --------------------------------------
# Add docs directory to path so we can import _scripts
sys.path.insert(0, str(Path(__file__).parent.resolve()))

try:
    # Import and run chart generator script
    from _scripts.generate_pd14_charts import main as charts_main
    print("Running generate_pd14_charts.py...")
    charts_main()
except Exception as e:
    print(f"Warning: Could not run generate_pd14_charts.py: {e}")

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["myst_parser",
              # "m2r2",
              "sphinx_gallery.gen_gallery",
              "sphinx_design",
              "sphinx.ext.mathjax",
              "sphinx.ext.autodoc",
              "sphinxcontrib.bibtex",
              "sphinx.ext.intersphinx"]

templates_path = ['_templates']
exclude_patterns = []
source_suffix = [".rst", ".md"]
myst_enable_extensions = ["colon_fence",
                          "dollarmath"]
bibtex_bibfiles = ["publications/publications.bib"]
bibtex_reference_style = "author_year"
bibtex_default_style = "unsrt"


class SortByYearDescending(BaseSortingStyle):
    def sort(self, entries):
        year_key = 'year'
        default_year = '0000'
        return sorted(entries,
                      key=lambda entry: entry.fields.get(year_key,
                                                         default_year),
                      reverse=True)


class UnsrtStyleByYear(UnsrtStyle):
    default_sorting_style = SortByYearDescending


def setup(app):
    from pybtex.plugin import register_plugin  # noqa: E402
    register_plugin('pybtex.style.formatting', 'unsrtyear', UnsrtStyleByYear)


sphinx_gallery_conf = {
     "examples_dirs": "../PyNEST/examples",   # path to your example scripts
     "gallery_dirs": "auto_examples",  # path to where to save gallery generated output
     "plot_gallery": False,
}

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "nest": ("https://nest-simulator.readthedocs.io/en/stable/", None),
    "nestml": ("https://nestml.readthedocs.io/en/latest/", None),
    "desktop": ("https://nest-desktop.readthedocs.io/en/latest/", None),
    "gpu": ("https://nest-gpu.readthedocs.io/en/latest/", None),
    "neat": ("https://nest-neat.readthedocs.io/en/latest/", None),
}
# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

pygments_style = "manni"
html_theme = 'sphinx_material'
html_static_path = ['_static']
html_theme_options = {
    # Set the name of the project to appear in the navigation.
    # Set you GA account ID to enable tracking
    # 'google_analytics_account': 'UA-XXXXX',
    # Specify a base_url used to generate sitemap.xml. If not
    # specified, then no sitemap will be built.
    "base_url": "https://microcircuit-pd14.readthedocs.io/en/latest/",
    "html_minify": False,
    "html_prettify": False,
    "css_minify": True,
    # Set the color and the accent color
    "color_primary": "orange",
    "color_accent": "white",
    "theme_color": "ff6633",
    "master_doc": False,
    # Set the repo location to get a badge with stats
    "repo_url": "https://github.com/INM-6/microcircuit-PD14-model/",
    "repo_name": "microcircuit-PD14",
    "nav_links": [{"href": "index", "internal": True, "title": "Docs home"}],
    # Visible levels of the global TOC; -1 means unlimited
    "globaltoc_depth": 1,
    # If False, expand all TOC entries
    "globaltoc_collapse": True,
    # If True, show hidden TOC entries
    "globaltoc_includehidden": True,
    "version_dropdown": False,
}

html_css_files = [
    "css/custom.css"]

# Custom sidebar templates, maps page names to templates.
html_sidebars = {"**": ["logo-text.html", "globaltoc.html", "localtoc.html", "searchbox.html"]}
