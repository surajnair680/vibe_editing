#!/bin/sh
# Caveat + Reenie Beanie (SIL OFL 1.1), pinned google/fonts commit. Fonts are kept in git too.
set -e
D=$(cd "$(dirname "$0")" && pwd)/fonts; mkdir -p "$D"
GF=https://raw.githubusercontent.com/google/fonts/86aced91de05cd4f96a06838124cca45be337b2b
get() { [ -s "$D/$1" ] && return 0; curl -fsSL -g --retry 2 -o "$D/$1" "$2"; echo "fonts/$1"; }
get Caveat.ttf "$GF/ofl/caveat/Caveat[wght].ttf"
get ReenieBeanie.ttf "$GF/ofl/reeniebeanie/ReenieBeanie.ttf"
