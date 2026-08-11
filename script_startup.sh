#!/bin/bash
# echo "Startup script executed at: $(date)" >> /home/pi/startup.log

# Optional delay (e.g. 5 seconds)
sleep 10

# Activate virtual environment
source $HOME/Nishad_env/bin/activate
# Run the Python program
python3 $HOME/Hb_meter/nishad_switch.py
