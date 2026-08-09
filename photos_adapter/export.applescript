on run arguments
    set assetIdentifier to item 1 of arguments
    set outputDirectory to item 2 of arguments
    tell application "Photos"
        set matches to every media item whose id is assetIdentifier
        if (count of matches) is 0 then error "Объект Photos не найден"
        export matches to POSIX file outputDirectory using originals false
    end tell
end run
