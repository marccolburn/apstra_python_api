from getpass import getpass
from requests import request
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from pprint import pprint
from jinja2 import Environment, FileSystemLoader, select_autoescape
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
    pdb.set_trace()
    response = request("POST", api_url, data=data, headers=headers, verify=False)
    if response.status_code != 202 and response.status_code != 201:
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
                if data_response.status_code != 202 and data_response.status_code != 204:
                    sys.exit('error deleting element')


def aos_create_data(var_data, template_name):
    '''Provides data structure and api path for creating elements'''
    template = env.get_template(template_name)
    data = template.render(var_data)
    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--create", help="create elements passed, asn_pools, ip_pools, vni_pools")
    parser.add_argument("--delete", help="delete elements passed, asn_pools, ip_pools")
    parser.add_argument("--get", help="get elements passed, asn_pools, ip_pools")
    parser.add_argument("--type", help="type of elements to pass, resources, design, etc.")
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
    ip_pool_api_url = api_base_url + 'resources/ip-pools'
    env = Environment(
            loader=FileSystemLoader("templates"),
            autoescape=select_autoescape()
    )
    if args.create:
        if args.type == 'resources':
            api_url = api_base_url + 'resources/{0}'.format(args.create.replace("_", "-"))
        elif args.type == 'design':
            api_url = api_base_url + 'design/{0}'.format(args.create.replace("_", "-"))
        if args.create == 'asn_pools':
            for asn_range in yaml_data['asn_ranges']:
                template_name = "create_asn_pools.j2"
                asn_create_data = aos_create_data(asn_range, template_name)
                asn_response = aos_put(api_url, head_w_token, asn_create_data)
        else:
            for pool in yaml_data[args.create]:
                template_name = "create_{0}.j2".format(args.create)
                create_data = aos_create_data(pool, template_name)
                response = aos_put(api_url, head_w_token, create_data)

    if args.delete:
        if args.type == 'resources':
            api_url = api_base_url + 'resources/{0}'.format(args.delete.replace("_", "-"))
        elif args.type == 'design':
            api_url = api_base_url + 'design/{0}'.format(args.delete.replace("_", "-"))
        if args.delete == 'asn_pools':
            aos_delete(api_url, head_w_token, yaml_data['asn_ranges'])
        else:
            aos_delete(api_url, head_w_token, yaml_data[args.delete])

    if args.get:
        if args.type == 'resources':
            api_url = api_base_url + 'resources/{0}'.format(args.get.replace("_", "-"))
        elif args.type == 'design':
            api_url = api_base_url + 'design/{0}'.format(args.get.replace("_", "-"))
        if args.get == 'asn_pools':
            asn_ranges = aos_get(api_url, head_w_token)
            pprint(asn_ranges.json())
        else:
            var_data = aos_get(api_url, head_w_token)
            pprint(var_data.json())
