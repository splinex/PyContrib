#!/usr/bin/env bash

ffmpeg -i $1 -vcodec copy -map 0:0 -map 0:1 -copyts -f mpegts $2 > $3 2>&1
