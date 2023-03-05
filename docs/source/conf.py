# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'DIP'
copyright = '2023, Ondrej Pego Jaura'
author = 'Ondrej Pego Jaura'
release = 'v0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx_rtd_theme',
    'sphinx.ext.autodoc'
]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ['_static']
html_logo = "_static/logo/dip_logo_64.png"
html_theme_options = {
    'logo_only': False,
    'display_version': True,
}
html_css_files = [
    'css/sphinxdoc.css'
]

# DIP Syntax Highlighter
import sys
sys.path.append("../../src")
from sphinx.highlighting import lexers
from dipsl.pygments.DIP_Lexer_Syntax import DIP_Lexer_Syntax
from dipsl.pygments.DIP_Lexer_Schema import DIP_Lexer_Schema
from dipsl.pygments.DIP_Lexer_Style import DIP_Lexer_Style, pygments_monkeypatch_style
pygments_monkeypatch_style("DIP_Lexer_Style", DIP_Lexer_Style)
pygments_style = 'DIP_Lexer_Style'
lexers['DIP'] = DIP_Lexer_Syntax(startinline=True, style=DIP_Lexer_Style)
lexers['DIPSchema'] = DIP_Lexer_Schema(startinline=True, style=DIP_Lexer_Style)

