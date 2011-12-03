@echo off
SET VAR_CD=%~dp0
del /q "%VAR_CD%\*.zip" > NUL 2>NUL
do_get.py