#!/bin/bash

set -e
cd "$(dirname "$(dirname "$(realpath "${BASH_SOURCE[0]}" )" )" )"

if [ -z "$1" -o -z "$2" ]
then
    echo "USAGE: $0 <scene-path> <scene-name>"
    exit 1
fi

SCENE_PATH="$1"
SCENE_NAME="$2"

.env/bin/manim -ql --save_sections "$SCENE_PATH" "$SCENE_NAME"