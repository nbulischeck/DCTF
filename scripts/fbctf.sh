#!/bin/bash
git clone https://github.com/facebook/fbctf
cd fbctf
source ./extra/lib.sh
quick_setup start_docker prod
set_password password ctf ctf fbctf $PWD
