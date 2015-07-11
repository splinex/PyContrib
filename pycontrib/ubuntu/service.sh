#!/usr/bin/env bash

set +e

sleep 10

source /home/human/.bashrc
export PYTHONPATH=$PYTHONPATH:/home/human/PyContrib
PYTHONPATH=$PYTHONPATH:/home/human/PyContrib

while true
do
	screen -X -S $1 quit
	sleep 5
	screen -d -m -S proxy python3 $2 --config $3
	inotifywait -e modify $3
done
