#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import requests

class Contrail_Json():
    def __init__(self, args_str = None):
        self._args = None
        self.global_defaults = {
            'keystone_api' : '172.27.113.85',
            'contrail_api' : '172.27.113.85',
            'username': 'admin',
            'password': 'juniper123',
            'tenant': "demo",
            'operation' : 'get',
            'body' : '',
            'api_dir' : '',
            'trace' : True,
        }
        self.parse_args(args_str, self.global_defaults)

    def parse_args(self, args_str, global_defaults):
        '''
        Eg. contrial-json - POST --contrail_api 172.27.113.85
        '''

        parser = argparse.ArgumentParser(description='Contrail REST/API handler')
        parser.add_argument('-k', '--keystone_api', dest='keystone_api', help='keystone API server address')
        parser.add_argument('-c', '--contrail_api', dest='contrail_api', help='Contrail API server address')
        parser.add_argument('-u', '--username', dest='username', help='Username')
        parser.add_argument('-p', '--password', dest='password',  help='Password')
        parser.add_argument('-t', '--tenant', dest='tenant',  help='Tenant name')
        parser.add_argument('-o', '--operation', dest='operation', help='Select get/post/put/delete')
        parser.add_argument('-b', '--body', dest='body', help='Set JSON message')
        parser.add_argument('-d', '--directory', dest='api_dir', help='Set API direcroty')
        parser.add_argument('-T', '--trace', dest='trace', help='Output trace')

        args = vars(parser.parse_args())
        self.create_parameter(args, global_defaults)

    def create_parameter(self, args, global_defaults):
        for k, v in args.iteritems():
            if v is not None: 
                global_defaults[k] = v

        self.get_auth_token(global_defaults)

    def get_auth_token(self, global_defaults):
        url = 'http://%s:5000/v2.0/tokens' % global_defaults['keystone_api']
        headers = {'Content-Type': 'application/json; charset=UTF-8'}
        data = '{"auth":{"passwordCredentials":{"username": "%s", "password": "%s"},"tenantName": "%s"}}' \
               % (global_defaults['username'], global_defaults['password'], global_defaults['tenant'])
        res = requests.post(url=url, data=data, headers=headers)
        if str(res.status_code) != '200':
            self.error_handler(res.status_code ,res.text)

        res = json.loads(res.text)
        auth_token = res["access"]["token"]["id"]

        self.get_contrail(auth_token, global_defaults)

    def get_contrail(self, auth_token, global_defaults):
        url = 'http://%s:8082/%s' % (global_defaults['contrail_api'], global_defaults['api_dir'])
        headers = {'Content-Type': 'application/json; charset=UTF-8', 'X-Auth-Token': auth_token}

        if global_defaults['operation'] == 'get':
            res = requests.get(url=url, headers=headers)
            if str(res.status_code) != '200':
                self.error_handler(res.status_code ,res.text)
            else:
                self.output_json(res.json(), global_defaults['trace'])

        if global_defaults['operation'] == 'delete':
            res = requests.delete(url=url, headers=headers)
            if str(res.status_code) != '200':
                self.error_handler(res.status_code ,res.text)
            else:
                print 'delete "%s" succesfully' % global_defaults['api_dir']

        if global_defaults['operation'] == 'post':
            if global_defaults['body'] is None:
                print 'Need JSON message'

            res = requests.post(url=url, headers=headers, data=global_defaults['body'])
            if str(res.status_code) != '200':
                self.error_handler(res.status_code ,res.text)
            else:
                self.output_json(res.json(), global_defaults['trace'])

        if global_defaults['operation'] == 'put':
            if global_defaults['body'] is None:
                print 'Need JSON message'

            res = requests.put(url=url, headers=headers, data=global_defaults['body'])
            if str(res.status_code) != '200':
                self.error_handler(res.status_code ,res.text)
            else:
                self.output_json(res.json(), global_defaults['trace'])

    def error_handler(self, code, status):
        print 'Error code "%s", %s' % (code, status)

    def output_json(self, data, trace):
        if trace == True:
            print json.dumps(data, sort_keys=True, indent=4)
        else:
            print json.dumps(data)


def main(args_str = None):
    Contrail_Json(args_str)

if __name__ == "__main__":
    main()
