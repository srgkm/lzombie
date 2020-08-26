#!/usr/bin/env bash

set -e

sudo -n true

apt-get update
apt-get install -y openssh-server cups supervisor git vim curl

# add-apt-repository -y ppa:deadsnakes/ppa
apt-get update
apt-get install -y python3 python3-pip python3-venv

cd /home/zombielavka

rm -rf /home/zombielavka/lzombie || true

git clone https://github.com/srgkm/lzombie.git

cd lzombie

python3 -m venv .venv

.venv/bin/pip install -U pip
.venv/bin/pip install -r requirements.txt

cd /home/zombielavka

chown -R "$(id -u)":"$(id -g)" lzombie

ln -sf /home/zombielavka/lzombie/config/supervisord/print-client.conf /etc/supervisor/conf.d/print-client.conf

supervisorctl reread
supervisorctl update
supervisorctl restart
supervisorctl status
