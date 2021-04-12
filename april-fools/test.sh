#!/bin/bash

notify-send "Now Playing" "Astolfo talks to you [10 hours ASMR]" --icon=folder-music

sleep 30

notify-send "System Warning" "Unexpected behaviour in system. Please check logs"

sleep 15

notify-send "System Error" "URGENT: Unexpected error in system. Please check logs" --urgency=critical

sleep 15

notify-send "System Shutdown Final Warning" "You've been hacked!!!" --urgency=critical

sleep 5

line=0
title=''

count=0

for j in $(cat data.txt | awk 'NR%12 > 9 || (NR%12 < 7 && NR%12 > 4) || NR%12 < 2' | sed -e 's/1/■/g' -e 's/0/_/g')
do
	if [[ $title == '' ]]
	then
		title=$j
	else
		notify-send $title $j
		title=''
		line=$line+1
	fi

	if [[ $line -eq 3 ]]
	then
		sleep 0.04
		line=0
	fi
	count=$count+1
	if [[ $count -eq 120 ]]
	then
		break
	fi
done
	
./main < input.txt


#for i in {1..100}
#do
#	notify-send "■■■■■■■■■■■■■■■■■■" "■■■■■■■■■■■■■■■■■■"
#	sleep 0.04
#done
