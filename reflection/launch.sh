#!/bin/bash

node ../server/server.js &
sleep 5
python3 send_data.py
