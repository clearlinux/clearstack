#!/bin/bash

# reset neutron services
neutron_services="neutron-server neutron-linuxbridge-agent \
 neutron-dhcp-agent neutron-metadata-agent neutron-l3-agent"
systemctl stop $neutron_services
systemctl disable $neutron_services

# Reset compute services
systemctl disable libvirtd.socket libvirtd.service nova-compute.service \
	  nova-network.service nova-metadata.{socket,service}
systemctl stop libvirtd.socket libvirtd.service nova-compute.service \
	  nova-network.service nova-metadata.{socket,service}

# Delete nova config file
rm -rf /etc/nova

# Update /etc/nova permissions
systemctl restart update-triggers.target

# Clean Bridges
ip link set br100 down
brctl delbr br100

# Restart network service
systemctl restart systemd-networkd

# Clean Nova data
rm -rf /var/lib/nova/CA/*
rm -rf /var/lib/nova/instances/*
rm -rf /var/lib/nova/keys/*
rm -rf /var/lib/nova/networks/*

# Clean Libvirt data
rm -rf /var/lib/libvirt/qemu/*.monitor
rm -rf /etc/libvirt/nwfilter/*
rm -rf /etc/libvirt/qemu/*

# Kill reamining qemu VMs
ps aux | grep qemu |  grep -v grep | awk '{print $2}' | xargs kill -9

# Kill all about dnsmasq
ps aux | grep dnsmasq |  grep -v grep | awk '{print $2}' | xargs kill -9

# Clean Logs
rm -rf /var/log/nova/*
rm -rf /var/log/libvirt/qemu/*
rm -rf /var/log/swupd/*
