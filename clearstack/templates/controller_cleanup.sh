#!/bin/bash

# reset neutron services
neutron_services="neutron-server neutron-linuxbridge-agent \
 neutron-dhcp-agent neutron-metadata-agent neutron-l3-agent"
systemctl stop $neutron_services
systemctl disable $neutron_services

# reset nova services
systemctl stop memcached uwsgi@nova-{api,metadata}.{service,socket} nova-cert \
                        nova-consoleauth nova-scheduler \
                        nova-conductor nova-novncproxy
systemctl disable memcached uwsgi@nova-{api,metadata}.{service,socket} nova-cert \
                        nova-consoleauth nova-scheduler \
                        nova-conductor nova-novncproxy
rm -rf /etc/nova

# reset glance services
systemctl stop glance-api glance-registry
systemctl disable glance-api glance-registry
rm -rf /etc/glance
rm -rf /var/lib/glance/images/*

# reset keystone services
systemctl stop httpd nginx uwsgi@keystone{admin,public}.{socket,service}
systemctl disable httpd nginx
rm -rf /etc/keystone
rm /etc/httpd/conf.d/wsgi-keystone.conf

# reset horizon
systemctl stop httpd nginx uwsgi@horizon.{socket,service}

# reset owners and permissions
systemctl restart update-triggers.target

# reset rabbitmq
systemctl stop rabbitmq-server
systemctl disable rabbitmq-server
rm -rf /etc/rabbitmq/rabbitmq.config
rm -rf /var/lib/rabbitmq/*
rm -rf /etc/hosts

# reset mariadb
systemctl stop mariadb
systemctl disable mariadb
rm -rf /etc/mariadb
rm -rf /var/lib/mysql

# Clean Logs
rm -rf /var/log/nova/*
rm -rf /var/log/keystone/*
rm -rf /var/log/glance/*
rm -rf /var/log/rabbitmq/*
rm -rf /var/log/httpd/*
rm -rf /var/log/swupd/*
