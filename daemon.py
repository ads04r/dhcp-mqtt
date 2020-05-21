#!/usr/bin/python3

from isc_dhcp_leases import Lease, IscDhcpLeases
import paho.mqtt.client as mqtt
import datetime, calendar, os, sys, json
from time import sleep

config_path = os.path.abspath(os.path.dirname(sys.argv[0]) + '/config.json')
if not(os.path.exists(config_path)):
	sys.stderr.write("Cannot find config file " + config_path + "\n")
	sys.exit(1)
with open(config_path) as data:
	config = json.load(data)
	data.close()
mqtt_host = config['mqtt']['host']
mqtt_topic = config['mqtt']['topic_prefix']

# Initialise

reader = IscDhcpLeases('/var/lib/dhcp/dhcpd.leases')
leases = []
messages = []
for lease in reader.get_current():
	mac = str(lease).replace(':', '')
	leases.append(mac)

while True:

	sleep(10)
	new_leases = []
	messages = []
	for lease in reader.get_current():
		mac = str(lease).replace(':', '')
		new_leases.append(mac)
	for mac in new_leases:
		if not(mac in leases):
			messages.append([mac, 'lease'])
	for mac in leases:
		if not(mac in new_leases):
			messages.append([mac, 'release'])
	leases = new_leases
	if len(messages) > 0:
		client = mqtt.Client("dhcp2mqtt")
		client.connect(mqtt_host)
		for message in messages:
			client.publish(mqtt_topic + message[0], message[1])
		client.disconnect()
