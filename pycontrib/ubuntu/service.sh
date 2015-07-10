#!/usr/bin/env bash

set +e

source ~/.bashrc

while true
do
	screen -X -S $2 quit
	screen -d -m -S proxy python3 $1 --config $2
	inotifywait -e modify $2
done
