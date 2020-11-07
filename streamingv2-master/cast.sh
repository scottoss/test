#!/bin/bash
set -exuo pipefail
if [[ ! $# -eq 1 ]]; then
  echo "usage: $0 <url>"
  exit 1
fi
OUT="icecast://source:d0ntHACKME@localhost:8000/stream"
ffmpeg -stats -report -i $1 -c:a libmp3lame -b:a 64k -legacy_icecast 1 -content_type audio/mpeg -ice_name "DemoStream" -f mp3 $OUT
