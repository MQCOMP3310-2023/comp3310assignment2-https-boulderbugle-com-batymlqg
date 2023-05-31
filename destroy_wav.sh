#!/bin/bash

server_url="http://127.0.0.1:8000/delete_wav_files"
content="1234"

while true; do
  curl -X POST -d "$content" $server_url
  sleep 1  # Wait for 1 second before sending the next request
done

