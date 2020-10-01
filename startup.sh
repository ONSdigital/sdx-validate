#!/bin/bash

if [ -z ${PORT+x} ]; 
then 
    export PORT=5000; 
fi

gunicorn -b 0.0.0.0:$PORT server:app
