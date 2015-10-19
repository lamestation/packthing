tell application "Finder"
    tell disk "${VOLUME}"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set the bounds of container window to {400, 100, 900, 434}
        set theViewOptions to the icon view options of container window
        set arrangement of theViewOptions to not arranged
        set icon size of theViewOptions to 72
        set background picture of theViewOptions to file ".background:${BACKGROUND}"
        make new alias file at container window to POSIX file "/Applications" with properties {name:"Applications"}
        set position of item "${BUNDLE}" of container window to {105, 180}
        set position of item "Applications" of container window to {395, 180}
        update without registering applications
        close
    end tell
end tell
