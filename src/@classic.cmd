@echo off
SET VAR_CD=%~dp0
del /q "%VAR_CD%\*.zip" > NUL 2>NUL
del /q "%VAR_CD%\*.rar" > NUL 2>NUL
python do_get.py addons-classic.json