import json

"""
	In order to develop on your machine, set beta and production to False.
	Make sure you do not commit any changes you make to this file, otherwise you will break the website.
"""
production = False
beta = False

# Read configurations
config = (open('pulleffect/config/prod_config.json') if production 
	else (open('pulleffect/config/beta_config.json') if beta else open('pulleffect/config/dev_config.json')))

# Export configurations
config = json.load(config)