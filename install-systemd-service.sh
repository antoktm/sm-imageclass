#!/bin/bash

if [ "$(id -u)" -ne 0 ]
  then echo "Please run as root"
  exit
fi

workdir="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
user_owner=$(stat -c '%U' $workdir/imageclass-server.py)
svc_file="/etc/systemd/system/imageclass-svr.script"

svc_script="[Unit]
Description=Image Classifier Server
After=network.target syslog.target

[Service]
ExecStart=$workdir/imageclass-server.py
Restart=always
User=$user_owner
WorkingDirectory=$workdir

[Install]
WantedBy=multi-user.target
"

if [ -f "$svc_file" ]; then
    echo "Installation failed. Service file already exists. Please check and remove $svc_file first."
    exit
else
    echo "$svc_script" > /etc/systemd/system/imageclass-svr.script
    echo "Installation finished"
    echo "Execute 'systemctl start imageclass-svr' to start the service"
fi
