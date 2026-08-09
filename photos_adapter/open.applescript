on run arguments
    set assetIdentifier to item 1 of arguments
    tell application "Photos"
        set matches to every media item whose id is assetIdentifier
        if (count of matches) is 0 then error "Объект Photos не найден"
        activate
        spotlight item 1 of matches
    end tell
end run
