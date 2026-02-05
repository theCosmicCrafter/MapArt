@echo off
if exist launch_silent.vbs (
    start wscript launch_silent.vbs
    exit
)
start "" /min npm start
exit
