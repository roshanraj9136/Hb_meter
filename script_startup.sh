#!/bin/bash
# echo "Startup script executed at: $(date)" >> /home/pi/startup.log

# Optional delay (e.g. 5 seconds)
sleep 10

# Activate virtual environment
source /home/hbmeter1/Nishad_env/bin/activate
# Run the Python program
python3 /home/hbmeter1/Hb_meter/nishad_switch.py
