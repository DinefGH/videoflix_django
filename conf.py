# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
import django


# Set the correct path to your project
sys.path.insert(0, os.path.abspath('../'))  # This should be the path to the root of your project
sys.path.insert(0, os.path.abspath('../videoflixbackend'))  # Add your Django app path

# Set the environment variable for Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'videoflixbackend.settings'  # Ensure the path matches your project

# Initialize Django
django.setup()


project = 'Videoflix'
copyright = '2024, Fabian'
author = 'Fabian'
release = '03.10.2024'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',            # Automatically generates documentation from docstrings
    'sphinx.ext.viewcode',           # Add links to highlighted source code
    'sphinx.ext.napoleon',           # Support for Google and NumPy style docstrings
    'sphinx_autodoc_typehints',      # Show type hints in the documentation
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']


