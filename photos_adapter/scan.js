const photos = Application('Photos');
const items = photos.mediaItems;
const identifiers = items.id();
const filenames = items.filename();
const dates = items.date();
const widths = items.width();
const heights = items.height();
const sizes = items.size();
const assets = [];

for (let index = 0; index < identifiers.length; index += 1) {
    assets.push({
        id: identifiers[index],
        name: filenames[index],
        created_at: dates[index] || '',
        width: widths[index] || 0,
        height: heights[index] || 0,
        size: sizes[index] || 0,
    });
}

JSON.stringify({status: 'authorized', assets: assets});
