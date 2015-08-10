#!/usr/bin/env bash

set +e

sleep 2

while true
do
	if inotifywait -e modify -t 20 $4
	then
		sleep 1
	else
		screen -X -S $3 quit
		sleep 5
		screen -d -m -S $3 ./command.sh $1 $2 $4
		sleep 5
	fi
done
