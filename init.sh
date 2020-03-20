#!/bin/bash

sudo -n true

apt-get update
apt-get install -y openssh-server cups supervisor git vim curl

add-apt-repository -y ppa:deadsnakes/ppa
apt-get update
apt-get install -y python3.6 python3.6-venv

cd || exit

git clone https://github.com/srgkm/lzombie.git

cd lzombie || exit

python3.6 -m venv .venv

.venv/bin/pip install -U pip
.venv/bin/pip install -r requirements.txt

cd || exit
chown -R "$(id -u)":"$(id -g)" lzombie

ln -s /home/zombielavka/lzombie/conf/supervisord/print-client.conf /etc/supervisor/conf.d/print-client.conf

supervisorctl reread
supervisorctl update
supervisorctl status
