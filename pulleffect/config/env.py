import json

"""
    In order to develop on your machine, set is_dev to True.
"""
is_dev = True

# Read configurations
config = json.load((open('pulleffect/config/config.json')))
