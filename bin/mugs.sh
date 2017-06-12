#!/bin/sh
python mugalyser_main.py --host mongodb://localhost:27017/MUGS   --admin --collect all --urlfile ../etc/mongodb_pro_groups $*
