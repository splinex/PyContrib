#!/usr/bin/env bash

set +e

source ~/.bashrc

while true
do
	screen -X -S $1 quit
	screen -d -m -S proxy python3 $2 --config $3
	inotifywait -e modify $3
done
