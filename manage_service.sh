#!/bin/bash
# Manage WorldQuant BRAIN Portal Background Daemon on macOS

PLIST_NAME="com.worldquant.brainportal.plist"
SOURCE_PLIST="/Users/priyanshukumar/Documents/antigravity/proud-nobel/$PLIST_NAME"
TARGET_DIR="$HOME/Library/LaunchAgents"
TARGET_PLIST="$TARGET_DIR/$PLIST_NAME"

case "$1" in
    install|start)
        echo "Installing and starting BRAIN Portal Background Service..."
        mkdir -p "$TARGET_DIR"
        cp "$SOURCE_PLIST" "$TARGET_PLIST"
        launchctl unload "$TARGET_PLIST" 2>/dev/null
        launchctl load -w "$TARGET_PLIST"
        echo "✅ Service active! Access portal at http://127.0.0.1:8080"
        ;;
    stop|uninstall)
        echo "Stopping BRAIN Portal Background Service..."
        launchctl unload "$TARGET_PLIST" 2>/dev/null
        rm -f "$TARGET_PLIST"
        echo "🛑 Service stopped and removed."
        ;;
    status)
        launchctl list | grep "com.worldquant.brainportal"
        if [ $? -eq 0 ]; then
            echo "🟢 Portal is RUNNING automatically in background."
        else
            echo "🔴 Portal is NOT running as launchd daemon."
        fi
        ;;
    *)
        echo "Usage: $0 {install|start|stop|status}"
        exit 1
        ;;
esac
