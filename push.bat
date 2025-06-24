@echo off
REM Script push force ke GitHub dengan pesan otomatis (Windows)
for /f "delims=" %%a in ('git config user.name') do set USERNAME=%%a
for /f "delims=" %%a in ('wmic os get localdatetime ^| findstr /r /v "^$"') do set DATETIME=%%a
set DATETIME=%DATETIME:~0,4%-%DATETIME:~4,2%-%DATETIME:~6,2% %DATETIME:~8,2%:%DATETIME:~10,2%:%DATETIME:~12,2%
set MESSAGE=update: auto-push %DATETIME% by %USERNAME%
git add .
git commit -m "%MESSAGE%"
git push --force 