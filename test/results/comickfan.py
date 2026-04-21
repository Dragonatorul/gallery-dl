# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import comickfan

__tests__ = (
    {
        "#url"     : "https://comickfan.com/manga/the-demonic-supreme-sword/chapter-1-dCJ0Mz11GQ",
        "#category": ("", "comickfan", "chapter"),
        "#class"   : comickfan.ComickfanChapterExtractor,
        "#pattern" : r"https://[a-z0-9]+\.cdncmk\.com/.*\.(webp|png|jpe?g|gif|avif|nl)",
        "#count"   : 25,
        "manga"    : "The Demonic Supreme Sword",
        "chapter"  : 1,
    },
    {
        "#url"     : "https://comickfan.com/manga/the-demonic-supreme-sword",
        "#category": ("", "comickfan", "manga"),
        "#class"   : comickfan.ComickfanMangaExtractor,
        "#pattern" : comickfan.ComickfanChapterExtractor.pattern,
        "#count"   : range(30, 200),
    },
)
