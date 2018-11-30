#!/bin/sh

. $HOME/.config/user-dirs.dirs

case $1 in
  uninstall)
    rm -f $XDG_DESKTOP_DIR/EAGLE.desktop
  ;;
  *) 
    cp -fv $HOME/.local/share/applications/EAGLE.desktop $XDG_DESKTOP_DIR
  ;;
esac

exit 0