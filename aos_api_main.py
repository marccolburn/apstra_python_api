from getpass import getpass
from aos.client import AosClient
from aos.resources import Range
from aos.aos import AosAPIError
import argparse
import urllib3
import yaml
import pdb

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def resource_pools(aos, type, mode, yaml_data):
    """
    Create, Delete, and GET Resource pools.
    Types: IPv4 Pools, ASN Pools, VNI Pools
    """

    if type == 'ip_pools' and mode == 'create':
        response = []
        for item in yaml_data['ip_pools']:
            response.append(aos.resources.ipv4_pools.create(name=item["name"], subnets=item["subnets"]))

    elif type == 'ip_pools' and mode == 'delete':
        response = []
        for item in yaml_data['ip_pools']:
            try:
                response.append(aos.resources.ipv4_pools.delete(item["name"]))
            except AosAPIError as e:
                print(e)

    elif type == 'ip_pools' and mode == 'get':
        ip_pools = list(aos.resources.ipv4_pools.iter_all())
        response = ip_pools
    
    elif type == 'asn_pools' and mode == 'create':
        response = []
        for item in yaml_data['asn_ranges']:
            response.append(aos.resources.asn_pools.create(name=item["name"], ranges=[Range(item["first"], item["last"])]))

    elif type == 'asn_pools' and mode == 'delete':
        response = []
        for item in yaml_data['asn_ranges']:
            try:
                response.append(aos.resources.asn_pools.delete(item["name"]))
            except AosAPIError as e:
                print(e)

    elif type == 'asn_pools' and mode == 'get':
        asn_pools = list(aos.resources.asn_pools.iter_all())
        response = asn_pools
    
    elif type == 'vni_pools' and mode == 'create':
        response = []
        for item in yaml_data['vni_pools']:
            response.append(aos.resources.vni_pools.create(name=item["name"], ranges=[Range(item["first"], item["last"])]))

    elif type == 'vni_pools' and mode == 'delete':
        response = []
        for item in yaml_data['vni_pools']:
            try:
                response.append(aos.resources.vni_pools.delete(item["name"]))
            except AosAPIError as e:
                print(e)

    elif type == 'vni_pools' and mode == 'get':
        vni_pools = list(aos.resources.vni_pools.iter_all())
        response = vni_pools

    return response


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--create", help="create elements passed, asn_pools, ip_pools, vni_pools")
    parser.add_argument("--delete", help="delete elements passed, asn_pools, ip_pools")
    parser.add_argument("--get", help="get elements passed, asn_pools, ip_pools")
    parser.add_argument("--type", help="type of elements to pass, resources, design, etc.")
    args = parser.parse_args()

    yaml_file = open('apstra_vars.yaml', 'r')
    yaml_data = yaml.load(yaml_file, Loader=yaml.Loader)
    yaml_file.close()

    AOS_IP = yaml_data['server_ip']
    AOS_PORT = yaml_data['server_port']
    AOS_USER = yaml_data['server_user']
    AOS_PW = getpass('AOS User Password: ')

    aos = AosClient(protocol="https", host=AOS_IP, port=AOS_PORT)
    aos.auth.login(AOS_USER, AOS_PW)

    if args.create:
        if args.create == 'asn_pools' or args.create == 'ip_pools' or args.create == 'vni_pools':
            type = args.create
            mode = "create"
            response = resource_pools(aos, type, mode, yaml_data)

    if args.delete:
        if args.delete == 'asn_pools' or args.delete == 'ip_pools' or args.delete == 'vni_pools':
            type = args.delete
            mode = "delete"
            response = resource_pools(aos, type, mode, yaml_data)

    if args.get:
        if args.get == 'asn_pools' or args.get == 'ip_pools' or args.get == 'vni_pools':
            type = args.get
            mode = "get"
            response = resource_pools(aos, type, mode, yaml_data)

    print(response)
