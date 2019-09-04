#!/bin/bash

#{   echo "This is the body message";   uuencode L.jpg L.jpg;   uuencode 240c.jpg 240c.jpg; } | mailx -s "test" cagnulein@gmail.com
attachments='{'
for file in people/*.jpg; do
    attachments="${attachments} uuencode '$file' '$file'; "
done
attachments="${attachments}} | mailx -s 'Persone in casa!' cagnulein@gmail.com"
echo ${attachments}
eval "$attachments"
