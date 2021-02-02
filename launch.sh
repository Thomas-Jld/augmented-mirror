#!/bin/bash

make launch &
sleep 5
cd apps &&
chromium index.html --start-fullscreen
