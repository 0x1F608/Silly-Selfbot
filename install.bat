echo off
cls
echo Starting installation...
pip install requests >nul
echo installed requests
pip install discord
pip uninstall discord
pip install discord.py==1.7.3
echo installed discord.py
pip install winotify
echo installed winotify
pip install colorama
echo installed colorama
pip install pystyle
echo installed pystyle
pip install websocket-client
echo installed websocket-client
pip install flask
echo installed flask
pip install gevent
echo installed gevent
pip install cryptography
echo installed cryptography

echo Installation done!
echo have fun using silly selfbot ;)
pause
