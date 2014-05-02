@echo off
rem Batch file to run Pyro4 name server

rem edit below changing 'hostname' to the name of your local machine
rem if python is not on your system path, edit 'python' to include full path to Python executable

cmd /K python -Wignore -m Pyro4.naming -n hostname