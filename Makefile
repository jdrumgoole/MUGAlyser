#
# Collect MUG data
#
PYTHON=python3
MAINCMD="mugalyser/mugalyser_main.py"
URLFILE="--urlfile etc/master_mug_list.txt"
COLLECTNOPRO="--collect nopro"

noproone:
	${PYTHON} ${MAINCMD} --database MUGS --drop --collect nopro --organizer_id 99473492 --urlfile etc/master_mug_list.txt

proone:
	${PYTHON} ${MAINCMD} --database MUGS --drop --collect pro --urlfile etc/master_mug_list.txt

pronoproone:
	${PYTHON} ${MAINCMD} --database MUGS --drop --collect all  --organizer_id 99473492 --urlfile etc/master_mug_list.txt

testcmd:
	@echo "python mugalyser/mugalyser_main.py  -h"
	${PYTHON} ${MAINCMD} -h
