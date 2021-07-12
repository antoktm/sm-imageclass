#!/bin/bash
{
    sleep 5s
    kill $$
} &

./imageclass-client.py $1
