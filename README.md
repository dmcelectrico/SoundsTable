# lavidamoderna_bot
Bot de Telegram con sonidos de la vida moderna. Basado en el proyecto de Xatpy/SoundsTable

[![Build Status](https://travis-ci.org/dmcallejo/lavidamoderna_bot.svg?branch=master)](https://travis-ci.org/dmcallejo/lavidamoderna_bot) [![Docker Automated build](https://img.shields.io/docker/automated/dmcallejo/lavidamoderna_bot.svg)](https://hub.docker.com/r/dmcallejo/lavidamoderna_bot/) [![Docker Build Status](https://img.shields.io/docker/build/dmcallejo/lavidamoderna_bot.svg)](https://hub.docker.com/r/dmcallejo/lavidamoderna_bot/) [![Docker Pulls](https://img.shields.io/docker/pulls/dmcallejo/lavidamoderna_bot.svg)](https://hub.docker.com/r/dmcallejo/lavidamoderna_bot)

All audios must be encoded using ffmpeg with these parameters:
```
ffmpeg -i $INPUT -map_metadata -1 -ac 1 -map 0:a -codec:a libopus -b:a 128k -vbr off -ar 48000 $OUTPUT
```
