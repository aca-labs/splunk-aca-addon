[aca_engine_api://<name>]
override_sourcetype = Override default sourcetype. Recommended to assist with later searches - set to something specific to query.  e.g. ACA_API_Modules, or ACA_API_Dynalite
api_endpoint = Endpoint to get bearer token from. e.g. https://localhost/auth/oauth/token
url_to_query = Will be the GET modules url from ACA API. e.g. https://localhost/control/api/modules
custom_input_ = Custom inputs as defined in Python script. Select 'No' unless calling /modules or /systems. Separates multi-events. To make own, edit inputs.conf or edit script for more control.
to_obscure = Replaces  a sensitive value (e.g. password for Booking modules) if included in results with "obscured".
client_id = Get this and following values from backoffice. Set up a user for this app. See ACA Engine administrator for assistance.
client_secret = 
username = 
password = 
authority = e.g. sgrp-nU3aYzXK0N
refresh_token_timer = Time in seconds for token to expire. Default is 14 days. Do not change unless you know what you're doing.