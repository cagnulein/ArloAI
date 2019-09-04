#!/bin/bash

LOCKFILE=/tmp/arloai.lck
if [ -e ${LOCKFILE} ] && kill -0 `cat ${LOCKFILE}`; then
    echo "already running"
    exit
fi

# make sure the lockfile is removed when we exit and then claim it
trap "rm -f ${LOCKFILE}; exit" INT TERM EXIT
echo $$ > ${LOCKFILE}

nice -n19 python3 arloai.py

if [[ `ls -ltr people/ | tail -n1 | grep index.html` ]]; then
	echo "no new people";
else
	if [[ `ls -ltr people | grep jpg` ]]; then
	        #echo "http://robertoviola.cloud:3001/" | mail -s "Persone a casa!" cagnulein@gmail.com
		#cd people/ && ../gallery_shell/gallery.sh -t arlo -d thumb/
		./send-multiple-image.sh && ./clean-people.sh
	else
		echo "no new people";
	fi
fi

rm -f ${LOCKFILE}
