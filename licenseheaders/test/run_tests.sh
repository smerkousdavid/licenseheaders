#!/bin/bash

printf "Running tests...\nJavascript test\n\n"

python ../licenseheaders.py -d "javascript" -t "mit" -y "2018" -o "David Smerkous" -n "Tests" -u "https://smerkous.com" -f 1

echo "Done!"