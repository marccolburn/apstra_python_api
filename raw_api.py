from getpass import getpass
from requests import request
import sys


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
    aos_server = '10.1.94.10'
    aos_user = 'admin'
    aos_pass = getpass('password: ')
    api_base_url = 'https://{0}/api/'.format(aos_server)
    head_w_token = aos_login(api_base_url, aos_user, aos_pass)
    print(head_w_token)
    asn_range = {
            'name': 'test_pool2',
            'first': 403,
            'last': 405
    }
    asn_create_data, asn_create_url = aos_asn_pool_create_data(api_base_url, asn_range)
    asn_response = aos_put(asn_create_url, head_w_token, asn_create_data)
    print(asn_response.status_code)
