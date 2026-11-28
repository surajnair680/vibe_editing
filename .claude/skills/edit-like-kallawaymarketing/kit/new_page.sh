#!/bin/sh
# Copy the Kallaway panel kit into a page folder: sh new_page.sh projects/<name>/mg/panel
# Gives <dest>/kallaway.css, kallaway.js, fonts/, bg/ and (if missing) a starter index.html from the example.
set -e
KIT="$(cd "$(dirname "$0")" && pwd)"; DEST="$1"; [ -n "$DEST" ] || { echo "usage: new_page.sh <dest>"; exit 1; }
mkdir -p "$DEST/fonts" "$DEST/bg"
cp "$KIT/kallaway.css" "$KIT/kallaway.js" "$DEST/"
cp "$KIT/../assets/fonts/"*.ttf "$DEST/fonts/"
cp "$KIT/../assets/backgrounds/"*.png "$DEST/bg/"
[ -f "$DEST/index.html" ] || cp "$KIT/example/index.html" "$DEST/index.html"
echo "kit copied to $DEST"
