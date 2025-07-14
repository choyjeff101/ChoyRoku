#!/bin/bash
cd /home/jeff/ChoyRoku
# Uncomment the next line if you use a virtual environment
source venv/bin/activate

exec gunicorn --config gunicorn.conf.py ChoyRoku:app
