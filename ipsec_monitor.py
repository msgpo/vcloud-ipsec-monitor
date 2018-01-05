#!/usr/bin/env python
# Created by Robin Ostlund <me@robinostlund.name>

import base64
import ssl
import urllib2
import sys
import argparse

import xml.etree.ElementTree as ET

class VcloudAPI(object):
    def __init__(self, username, password, org, url):
        self.vcloud_user = username
        self.vcloud_pass = password
        self.vcloud_org = org
        self.vcloud_url = url
        self.urllib_timeout = 30 # seconds
        self.ssl_context = ssl._create_unverified_context()

    def _request_vcloud_session(self):
        url = self.vcloud_url + '/api/sessions'
        login = base64.b64encode('%s@%s:%s' % (self.vcloud_user, self.vcloud_org, self.vcloud_pass))
        header = {
            'Authorization': 'Basic %s' % (login),
            'Accept': 'application/*+xml;version=5.5',
            'X-Requested-With' : 'urllib2'
        }
        request = urllib2.Request(url = url, data = '', headers = header) # data must be something to be a post
        request.get_method = lambda: 'POST'
        response = urllib2.urlopen(request, timeout = self.urllib_timeout, context = self.ssl_context)
        self.vcloud_session_id = response.info().getheader('x-vcloud-authorization')
        self.vcloud_session_id_decoded = base64.b64decode(self.vcloud_session_id)
        resp = response.read()
        code = response.getcode()
        headers = response.info()
        if code == 200:
            return True
        else:
            print("ERROR: Could not login to %s" % (self.vcloud_url))
            return False

    def _delete_vcloud_session(self):
        url = self.vcloud_url + '/api/session'
        header = {
            'x-vcloud-authorization': self.vcloud_session_id,
            'X-Requested-With' : 'urllib2',
            'Accept': 'application/*+xml;version=5.5'
        }
        request = urllib2.Request(url = url, data = '', headers = header)
        request.get_method = lambda: 'DELETE'
        response = urllib2.urlopen(request, timeout = self.urllib_timeout, context = self.ssl_context)
        resp = response.read()
        code = response.getcode()
        headers = response.info()
        if code == 204:
            return True
        else:
            print("ERROR: Could not logout from %s" % (self.vcloud_url))
            return False

    def _get_vcloud_data(self, url):
        header = {
            'Accept': 'application/*+xml;version=5.5',
            'x-vcloud-authorization': self.vcloud_session_id,
        }

        request = urllib2.Request(url = url, data = '', headers = header)
        request.get_method = lambda: 'GET'
        response = urllib2.urlopen(request, timeout = self.urllib_timeout, context = self.ssl_context)

        resp = response.read()
        code = response.getcode()
        headers = response.info()

        return headers, code, resp

    def _get_ipsec_vpn_tunnel_status(self):
        status = True
        url = "%s/api/query?type=edgeGateway&format=records" % (self.vcloud_url)
        headers, code, resp = self._get_vcloud_data(url)
        edge_gateway_list_in_xml = ET.fromstring(resp)

        for edge in edge_gateway_list_in_xml.findall('.//{http://www.vmware.com/vcloud/v1.5}EdgeGatewayRecord'):
            # enable for debug
            #ET.dump(edge)

            url = edge.attrib['href']
            headers, code, resp = self._get_vcloud_data(url)
            edge_gateway_in_xml = ET.fromstring(resp)

            # enable for debug
            #ET.dump(edge_gateway_in_xml)

            for elem in edge_gateway_in_xml.findall('.//{http://www.vmware.com/vcloud/v1.5}Tunnel'):
                tunnel_name = elem.find('.//{http://www.vmware.com/vcloud/v1.5}Name').text
                tunnel_is_operational = elem.find('.//{http://www.vmware.com/vcloud/v1.5}IsOperational').text
                tunnel_is_enabled = elem.find('.//{http://www.vmware.com/vcloud/v1.5}IsEnabled').text
                tunnel_peer_ip = elem.find('.//{http://www.vmware.com/vcloud/v1.5}PeerIpAddress').text
                if tunnel_is_operational and tunnel_is_enabled:
                    print("INFO: Tunnel %s to %s is UP (status: enabled)" % (tunnel_name.lower(), tunnel_peer_ip))
                else:
                    print("ERROR: Tunnel %s to %s is DOWN (status: enabled)" % (tunnel_name.lower(), tunnel_peer_ip))
                    status = False

                if not tunnel_is_enabled:
                    print("INFO: Tunnel %s to %s is DOWN (status: disabled)" % (tunnel_name.lower(), tunnel_peer_ip))

        return status

def main():
    parser = argparse.ArgumentParser()
    required_argument = parser.add_argument_group('required arguments')
    required_argument.add_argument('-u', '--username', dest='vcloud_username', help='Specify your vcloud username here', required = True)
    required_argument.add_argument('-p', '--password', dest='vcloud_password', help='Specify your vcloud password here', required = True)
    required_argument.add_argument('-o', '--organisation', dest='vcloud_organisation', help='Specify your vcloud organisation here', required = True)
    required_argument.add_argument('-v', '--url', dest='vcloud_url', help='Specify your vcloud url here', required=True)
    args = parser.parse_args()


    vc = VcloudAPI(args.vcloud_username, args.vcloud_password, args.vcloud_organisation, args.vcloud_url)

    # login to vcloud
    vc._request_vcloud_session()

    # get ipsec status
    status = vc._get_ipsec_vpn_tunnel_status()

    # logout from vcloud
    vc._delete_vcloud_session()

    # return correct exitcode
    if not status:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
