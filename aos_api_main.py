from getpass import getpass
from requests import request
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from pprint import pprint
import requests
import sys
import yaml
import json
import pdb
import argparse

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def aos_login(api_base_url, aos_user, aos_pass):
    '''AOS API Login Function, returns headers with auth token embedded'''
    url = '{0}user/login'.format(api_base_url)
    headers = {'Content-Type':"application/json", "Cache-Control":"no-cache" }
    data = '''
        {{
         "username":"{0}",
         "password":"{1}"
        }}
           '''.format(aos_user, aos_pass)
    response = request("POST", url, data=data, headers=headers, verify=False)
    if response.status_code != 201:
        sys.exit('error: authentication failed')
    auth_token = response.json()['token']
    headers = {'AuthToken':auth_token, 'Content-Type':"application/json", "Cache-Control":"no-cache" }
    return headers

def aos_put(api_url, headers, data):
    '''PUT against API resource to create new item'''
    response = request("POST", api_url, data=data, headers=headers, verify=False)
    if response.status_code != 202:
        sys.exit('error: data post failed')
    return response

def aos_get(api_url, headers):
    '''GET against API resource to get information'''
    response = request("GET", api_url, headers=headers, verify=False)
    if response.status_code != 200:
        sys.exit('error')
    return response

def aos_delete(api_url, headers, delete_pending_data):
    '''Pass data to be deleted'''
    data_response = request("GET", api_url, headers=headers, verify=False)
    if data_response.status_code != 200:
        sys.exit('error')
    
    json_data = data_response.json()
    for item in json_data['items']:
        for data in delete_pending_data:
            if item['display_name'] == data['name']:
                delete_url = '{0}/{1}'.format(api_url, item['id'])
                data_response = request("DELETE", delete_url, headers=headers, verify=False)
                if data_response.status_code != 202:
                    sys.exit('error deleting element')


def aos_asn_pool_create_data(api_base_url, asn_range):
    '''Provides data structure and api path for creating ASN Pools'''
    data = '''
        {{
         "display_name":"{0}",
         "ranges": [
           {{
             "first": "{1}",
             "last": "{2}"
           }}
        ]
        }}
           '''.format(asn_range['name'], asn_range['first'], asn_range['last'])

    api_url = '{0}resources/asn-pools'.format(api_base_url)
    return data, api_url


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--create", help="create elements passed, asn_pools")
    parser.add_argument("--delete", help="delete elements passed, asn_pools")
    parser.add_argument("--get", help="get elements passed, asn_pools")
    args = parser.parse_args()
    aos_server = '10.1.94.10'
    aos_user = 'admin'
    aos_pass = getpass('password: ')
    api_base_url = 'https://{0}/api/'.format(aos_server)
    head_w_token = aos_login(api_base_url, aos_user, aos_pass)
    yaml_file = open('apstra_vars.yaml', 'r')
    yaml_data = yaml.load(yaml_file, Loader=yaml.Loader)
    yaml_file.close()
    asn_api_url = api_base_url + 'resources/asn-pools'
    if args.create and args.create == 'asn_pools':
        for asn_range in yaml_data['asn_ranges']:
            asn_create_data, asn_create_url = aos_asn_pool_create_data(api_base_url, asn_range)
            asn_response = aos_put(asn_create_url, head_w_token, asn_create_data)

    if args.delete and args.delete == 'asn_pools':
        aos_delete(asn_api_url, head_w_token, yaml_data['asn_ranges'])

    if args.get and args.get == 'asn_pools':
        asn_ranges = aos_get(asn_api_url, head_w_token)
        pprint(asn_ranges.json())
