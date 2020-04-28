#encoding = utf-8

import os
import sys
import time
import datetime
import json

def validate_input(helper, definition):
    """Implement your own validation logic to validate the input stanza configurations"""
    # This example accesses the modular input variable
    # get_or_post = definition.parameters.get('get_or_post', None)
    # api_endpoint = definition.parameters.get('api_endpoint', None)
    # url_to_query = definition.parameters.get('url_to_query', None)
    # client_id = definition.parameters.get('client_id', None)
    # client_secret = definition.parameters.get('client_secret', None)
    # grant_type = definition.parameters.get('grant_type', None)
    # scope = definition.parameters.get('scope', None)
    # username = definition.parameters.get('username', None)
    # password = definition.parameters.get('password', None)
    # authority = definition.parameters.get('authority', None)
    pass

def collect_events(helper, ew):
    get_or_post = "GET"
    override_sourcetype = helper.get_arg('override_sourcetype')
    api_endpoint = helper.get_arg('api_endpoint')
    url_to_query = helper.get_arg('url_to_query')
    opt_custom_input_ = helper.get_arg('custom_input_')
    client_id = helper.get_arg('client_id')
    client_secret = helper.get_arg('client_secret')
    to_obscure = helper.get_arg('to_obscure')
    grant_type = "password"
    scope = "public"
    username = helper.get_arg('username')
    password = helper.get_arg('password')
    authority = helper.get_arg('authority')
    refresh_token_timer = helper.get_arg('refresh_token_timer')
    
    """ Acquire bearer token (first try loading from KV store) """
    
    token = helper.get_check_point('token')
    created_at = helper.get_check_point('created_at')
    refresh_token = helper.get_check_point('refresh_token')
    
    response = ""

    # if no token properly stored
    if ((token is None) or (created_at is None) or (refresh_token is None)):
        payload={"grant_type":grant_type,"username":username,"password":password,"authority":authority,"client_id":client_id,"client_secret":client_secret,"scope":scope}
        response = helper.send_http_request(api_endpoint, "POST", parameters=None, payload=payload, headers=None, cookies=None, verify=False, cert=None, timeout=None, use_proxy=True)
        
        token = json.loads(response.text)['access_token']
        created_at = json.loads(response.text)['created_at']
        refresh_token = json.loads(response.text)['refresh_token']
        
        helper.save_check_point('token', token)
        helper.save_check_point('created_at', created_at)
        helper.save_check_point('refresh_token', refresh_token)
        
    # if token close to expiry (+-2 hrs) get new token
    elif ((abs(time.time() - int(created_at)) >= (60*60*2 + int(refresh_token_timer))) and (refresh_token is not None)):
        payload={"grant_type":"refresh_token","refresh_token":refresh_token,"client_id":client_id,"client_secret":client_secret}
        response = helper.send_http_request(api_endpoint, "POST", parameters=None, payload=payload, headers=None, cookies=None, verify=False, cert=None, timeout=None, use_proxy=True)
        
        eventmod = helper.new_event(source=helper.get_input_type(), index=helper.get_output_index(), sourcetype=override_sourcetype, data=refresh_token, done=True, unbroken=True)
        ew.write_event(eventmod)
        
        token = json.loads(response.text)['access_token']
        created_at = json.loads(response.text)['created_at']
        refresh_token = json.loads(response.text)['refresh_token']
        
        helper.save_check_point('token', token)
        helper.save_check_point('created_at', created_at)
        helper.save_check_point('refresh_token', refresh_token)
        
    # error check
    if ("error" in response):
        helper.log_error("Trying again. Received: " + response)
        payload={"grant_type":grant_type,"username":username,"password":password,"authority":authority,"client_id":client_id,"client_secret":client_secret,"scope":scope}
        response = helper.send_http_request(api_endpoint, "POST", parameters=None, payload=payload, headers=None, cookies=None, verify=False, cert=None, timeout=None, use_proxy=True)
        
        token = json.loads(response.text)['access_token']
        created_at = json.loads(response.text)['created_at']
        refresh_token = json.loads(response.text)['refresh_token']
        
        helper.save_check_point('token', token)
        helper.save_check_point('created_at', created_at)
        helper.save_check_point('refresh_token', refresh_token)
        
    helper.log_info("Using token " + token + " created at " + str(created_at) + " with refresh token " + refresh_token + " to access ACA Engine API");
        
    """ Formulate a GET API request """
    
    head = {'Authorization': 'Bearer ' + token}
    
    responsereq = helper.send_http_request(url_to_query, "GET", parameters=None, payload=None, headers=head, cookies=None, verify=False, cert=None, timeout=None, use_proxy=True)
    helper.log_info("Received: " + str(responsereq.status_code) + " " + responsereq.text)
    responsereq = responsereq.json()
    
    """ Output options: add option below if needed.
    Suggest if(str(url_to_query).endswith("INSERTHERE")): do x approach """
    
    """ Break multiline event into multiple events and add time field """
    if (opt_custom_input_ == "modules"):
        count = responsereq['total'] - 1
        while count > -1:
            responsereq['results'][count]['time'] = str(datetime.datetime.now())
            data_out=json.dumps(responsereq['results'][count])
            if (len(to_obscure)>1):
                data_out = data_out.replace(to_obscure,"obscured")
            eventmod = helper.new_event(source=helper.get_input_type(), index=helper.get_output_index(), sourcetype=override_sourcetype, data=data_out.replace(" u\'","\'").replace("\'", "\""), done=True, unbroken=True)
            ew.write_event(eventmod)
            count = count - 1
            
            
    elif (opt_custom_input_ == "systems"):
        count = responsereq['total'] - 1
        while count > -1:
            responsereq['results'][count]['time'] = str(datetime.datetime.now())
            data_out=json.dumps(responsereq['results'][count])
            if (len(to_obscure)>1):
                data_out = data_out.replace(to_obscure,"obscured")
            eventmod = helper.new_event(source=helper.get_input_type(), index=helper.get_output_index(), sourcetype=override_sourcetype, data=data_out.replace(" u\'","\'").replace("\'", "\""), done=True, unbroken=True)
            ew.write_event(eventmod)
            count = count - 1
            
    else:
        data_out=json.dumps(responsereq)
        responsereq['time'] = str(datetime.datetime.now())
        if (len(to_obscure)>1):
            data_out = data_out.replace(to_obscure,"obscured")
        eventmod = helper.new_event(source=helper.get_input_type(), index=helper.get_output_index(), sourcetype=override_sourcetype, data=data_out.replace(" u\'","\'").replace("\'", "\""), done=True, unbroken=True)
        ew.write_event(eventmod)
        