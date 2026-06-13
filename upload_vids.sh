#!/bin/bash
FOLDER="/home/hbmeter1/Hb_meter/Data/vids"
REMOTE="sandy:hbmeter1_shaheeds"

/usr/bin/rclone copy "$FOLDER" "$REMOTE" --ignore-existing --log-file=/home/hbmeter1/upload.log --log-level=INFO
