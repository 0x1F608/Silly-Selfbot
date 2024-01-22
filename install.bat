echo off
cls
echo Starting installation...
pip install requests >nul
echo installed requests
pip install discord >nul
pip uninstall discord >nul
pip install discord.py==1.7.3 >nul
echo installed discord.py
pip install winotify >nul
echo installed winotify 
pip install colorama >nul
echo installed colorama
pip install pystyle >nul
echo installed pystyle
pip install websocket-client >nul
echo installed websocket-client
pip install flask >nul
echo installed flask
pip install gevent >nul
echo installed gevent
pip install cryptography >nul
echo installed cryptography
echo.
echo.
echo Installation done!
echo have fun using silly selfbot ;)
pause
