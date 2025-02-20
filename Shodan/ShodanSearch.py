#!/usr/bin/env python

# Script for interacting with Shodan's API and searching it.

# In case you get an import error for netaddr or shodan, run:
# apt-get install python-shodan python-netaddr

import argparse
from netaddr import IPNetwork
import os
import re
import shodan
import sys


def cli_parser():

    # Command line argument parser
    parser = argparse.ArgumentParser(
        add_help=False,
        description="ShodanSearch is a tool for searching shodan via its API.")
    parser.add_argument(
        "-search", metavar="Apache server", default=False,
        help="Use this when searching Shodan for a string.")
    parser.add_argument(
        "-f", metavar="ips.txt", default=None,
        help="File containing IPs to search shodan for.")
    parser.add_argument(
        "-ip", metavar='192.168.1.1', default=False,
        help="Used to return results from Shodan about a specific IP.")
    parser.add_argument(
        "-cidr", metavar='192.168.1.0/24', default=False,
        help="Used to return results from Shodan about a specific CIDR range.")
    parser.add_argument(
        "--hostnameonly", action='store_true',
        help="[Optional] Only provide results with a Shodan stored hostname.")
    parser.add_argument(
        "--page", metavar='1', default=1,
        help="Page number of results to return (default 1 (first page)).")
    parser.add_argument(
        '-h', '-?', '--h', '-help', '--help', action="store_true",
        help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.h:
        parser.print_help()
        sys.exit()

    return args.search, args.ip, args.cidr, args.hostnameonly, args.page, args.f


def create_shodan_object():
    # Add your shodan API key here
    api_key = "fwpsFkHzz3dLI8BysZyYQ9CUexcdWVGq"

    shodan_object = shodan.Shodan(api_key)

    return shodan_object


def shodan_cidr_search(shodan_search_object, shodan_search_cidr, input_file_ips):

    title()

    if shodan_search_cidr is not False:

        if not validate_cidr(shodan_search_cidr):
            print("[*] ERROR: Please provide valid CIDR notation!")
            sys.exit()

        else:

            print("[*] Searching Shodan for info about " + shodan_search_cidr)

            # Create cidr notated list
            network = IPNetwork(shodan_search_cidr)

    elif input_file_ips is not False:
        try:
            with open(input_file_ips, 'r') as ips_provided:
                network = ips_provided.readlines()
        except IOError:
            print("[*] ERROR: You didn't provide a valid input file.")
            print("[*] ERROR: Please re-run and provide a valid file.")
            sys.exit()

    # search shodan for each IP
    for ip in network:

        print("\n[*] Searching specifically for: " + str(ip))
        try:
            # Search Shodan
            result = shodan_search_object.host(ip)

            # Display basic info of result
            print("\n*** RESULT ***")
            print("IP: " + result['ip'])
            print("Country: " + result['country_name'])
            if result['city'] is not None:
                print("City: " + result['city'])
            print("\n")

            # Loop through other info
            for item in result['data']:
                print("Port: " + str(item['port']))
                print("Banner: " + item['data'])

        except Exception as e:
            if str(e).strip() == "API access denied":
                print("You provided an invalid API Key!")
                print("Please provide a valid API Key and re-run!")
                sys.exit()
            elif str(e).strip() == "No information available for that IP.":
                print("No information is available for " + str(ip))
            else:
                print("[*]Unknown Error: " + str(e))


def shodan_ip_search(shodan_search_object, shodan_search_ip):

    title()

    if validate_ip(shodan_search_ip):

        print("[*] Searching Shodan for info about " + shodan_search_ip + "...")

        try:
            # Search Shodan
            result = shodan_search_object.host(shodan_search_ip)

            # Display basic info of result
            print("\n*** RESULT ***")
            print("IP: " + str(result['ip']))
            print("Country: " + result['country_name'])
            if result['city'] is not None:
                print("City: " + result['city'])
            print("\n")

            # Loop through other info
            for item in result['data']:
                print("Port: " + str(item['port']))
                print("Banner: " + item['data'])

        except Exception as e:
                if str(e).strip() == "API access denied":
                    print("You provided an invalid API Key!")
                    print("Please provide a valid API Key and re-run!")
                    sys.exit()
                elif str(e).strip() == "No information available for that IP.":
                    print("No information on Shodan about " +\
                        str(shodan_search_ip))
                else:
                    print("[*]Unknown Error: " + str(e))

    else:
        print("[*]ERROR: You provided an invalid IP address!")
        print("[*]ERROR: Please re-run and provide a valid IP.")
        sys.exit()


def shodan_string_search(shodan_search_object, shodan_search_string,
                         hostname_only, page_to_return):

    title()

    # Try/catch for searching the shodan api
    print("[*] Searching Shodan...\n")

    try:
        # Time to search Shodan
        results = shodan_search_object.search(
            shodan_search_string, page=page_to_return)

        if not hostname_only:
            print("Total number of results back: " +\
                str(results['total']) + "\n")

        for result in results['matches']:
            if hostname_only:
                for item in result['hostnames']:
                    if item is None:
                        pass
                    else:
                        print("*** RESULT ***")
                        print("IP Address: " + result['ip'])
                        if result['country_name'] is not None:
                            print("Country: " + result['country_name'])
                        if result['updated'] is not None:
                            print("Last updated: " + result['updated'])
                        if result['port'] is not None:
                            print("Port: " + str(result['port']))
                        print("Data: " + result['data'])
                        for item in result['hostnames']:
                            print("Hostname: " + item)
                        print
            else:
                print("*** RESULT ***")
                print("IP Address: " + result['ip'])
                if result['country_name'] is not None:
                    print("Country: " + result['country_name'])
                if result['updated'] is not None:
                    print("Last updated: " + result['updated'])
                if result['port'] is not None:
                    print("Port: " + str(result['port']))
                print("Data: " + result['data'])
                for item in result['hostnames']:
                    print("Hostname: " + item)
                print

    except Exception as e:
        if str(e).strip() == "API access denied":
            print("You provided an invalid API Key!")
            print("Please provide a valid API Key and re-run!")
            sys.exit()


def title():
    os.system('clear')
    print("""____  _               _             _____      
                / ___|| |__   ___   __| | __ _ _ __
                \___ \| '_ \ / _ \ / _` |/ _` | '_ \  
                 ___) | | | | (_) | (_| | (_| | | | |  
                |____/|_| |_|\___/ \__,_|\__,_|_| |_|
                                               Search """)

    return


def validate_cidr(val_cidr):
    cidr_re = re.compile(r'^(\d{1,3}\.){0,3}\d{1,3}/\d{1,2}$')
    if cidr_re.match(val_cidr):
        ip, mask = val_cidr.split('/')
        if validate_ip(ip):
            if int(mask) > 32:
                return False
        else:
            return False
        return True
    return False


def validate_ip(val_ip):
    ip_re = re.compile(r'^(\d{1,3}\.){0,3}\d{1,3}$')
    if ip_re.match(val_ip):
        quads = (int(q) for q in val_ip.split('.'))
        for q in quads:
            if q > 255:
                return False
        return True
    return False


if __name__ == '__main__':

    # Parse command line options
    search_string, search_ip, search_cidr, search_hostnameonly,\
        search_page_number, search_file = cli_parser()

    # Create object used to search Shodan
    shodan_api_object = create_shodan_object()

    # Determine which action will be performed
    if search_string is not False:
        shodan_string_search(shodan_api_object, search_string,
                             search_hostnameonly, search_page_number)

    elif search_ip is not False:
        shodan_ip_search(shodan_api_object, search_ip)

    elif search_cidr is not False or search_file is not None:
        shodan_cidr_search(shodan_api_object, search_cidr, search_file)

    else:
        print("You didn't provide a valid option!.See options available with -h option")
