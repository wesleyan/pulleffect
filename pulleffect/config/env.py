import json

"""
    In order to develop on your machine, set beta and production to False.
    Make sure you do not commit any changes you make to this file,
    otherwise you will break the website.
"""
is_production = False
is_beta = False

# Read configurations
config = json.load((open('pulleffect/config/config.json')))
