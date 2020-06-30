#!/bin/bash
echo "Building File using: "
echo $CONDA_DEFAULT_ENV
pyinstaller --clean --onefile --add-data="config/config.json:config" app.py 
cp config/praw.ini dist/praw.ini
echo "File built to dist/app"
