# vcloud-ipsec-monitor
Simple script that can be used for monitor ipsec status of a vcloud ipsec tunnel.

#### Requirements
- python2
- ssl
- urllib2

#### Howto
Example:
```sh
$ ./ipsec_monitor.py -u <my_vcloud_username> -p <my_vcloud_password -o <my_vcloud_organisation> -v <my_vcloud_url>
INFO: Tunnel test to 8.8.8.8 is UP (status: enabled)
```

Help:
```sh
$ ./ipsec_monitor.py -h
usage: ipsec_monitor.py [-h] -u VCLOUD_USERNAME -p VCLOUD_PASSWORD -o
                        VCLOUD_ORGANISATION -v VCLOUD_URL

optional arguments:
  -h, --help            show this help message and exit

required arguments:
  -u VCLOUD_USERNAME, --username VCLOUD_USERNAME
                        Specify your vcloud username here
  -p VCLOUD_PASSWORD, --password VCLOUD_PASSWORD
                        Specify your vcloud password here
  -o VCLOUD_ORGANISATION, --organisation VCLOUD_ORGANISATION
                        Specify your vcloud organisation here
  -v VCLOUD_URL, --url VCLOUD_URL
                        Specify your vcloud url here
```

