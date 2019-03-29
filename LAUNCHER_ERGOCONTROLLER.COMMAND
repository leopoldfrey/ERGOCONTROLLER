#!/bin/sh
echo Starting ErgoController
cd $(dirname $0)/src
python3 -W ignore ./ErgoController.py
echo Done