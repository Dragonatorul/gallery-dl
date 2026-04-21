# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://comickfan.com/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text


class ComickfanBase():
    """Base class for comickfan.com extractors"""
    category = "comickfan"
    root = "https://comickfan.com"

    def __init__(self, match):
        super().__init__(match)
        self.page_url = self.url


class ComickfanChapterExtractor(ComickfanBase, ChapterExtractor):
    """Extractor for comickfan.com manga chapters"""
    pattern = (r"https?://comickfan\.com/manga/([\w-]+)/"
               r"chapter-([\d.]+)-([A-Za-z0-9_-]{10})/?$")
    example = ("https://comickfan.com/manga/"
               "the-demonic-supreme-sword/chapter-1-dCJ0Mz11GQ")

    def metadata(self, page):
        # Extract from window.chapter_data JS object
        data_str = text.extr(page, "window.chapter_data =", "</script>")
        data = {}
        if data_str:
            # Try to extract keys manually to avoid JSON errors due to comments
            for key in ("comic_id", "chapter_id", "comic_name",
                        "chapter_name", "chapter_slug"):
                val = text.extr(data_str, f'"{key}": "', '"')
                if val:
                    data[key] = val

        manga_title = data.get("comic_name") or text.extr(
            page, '<meta property="og:title" content="', '"')
        if manga_title:
            manga_title = manga_title.replace(" - ComicK Fanmade", "").strip()
            if manga_title.startswith("Chapter "):
                manga_title = manga_title.partition(" - ")[2]

        chapter = self.groups[1]
        chapter_major, sep, chapter_minor = chapter.partition(".")

        return {
            "manga"        : manga_title,
            "manga_id"     : data.get("comic_id"),
            "manga_slug"   : self.groups[0],
            "chapter"      : text.parse_int(chapter_major),
            "chapter_minor": sep + chapter_minor,
            "chapter_id"   : data.get("chapter_id"),
            "chapter_slug" : data.get("chapter_slug"),
            "title"        : data.get("chapter_name"),
        }

    def images(self, page):
        # Images are embedded as <img> tags
        # They usually have class 'object-cover mx-auto'
        # and are served from meo.cdncmk.com or meo2.cdncmk.com
        found = False
        for img_tag in text.extract_iter(page, "<img", ">"):
            if "object-cover" in img_tag and "mx-auto" in img_tag:
                src = text.extr(img_tag, 'src="', '"') or \
                    text.extr(img_tag, "src='", "'")
                if src:
                    found = True
                    yield src, {"referer": self.url}

        if not found:
            # Fallback: look for meo*.cdncmk.com URLs in <img> tags
            for img_tag in text.extract_iter(page, "<img", ">"):
                if "cdncmk.com" in img_tag:
                    src = text.extr(img_tag, 'src="', '"') or \
                        text.extr(img_tag, "src='", "'")
                    if src:
                        yield src, {"referer": self.url}


class ComickfanMangaExtractor(ComickfanBase, MangaExtractor):
    """Extractor for comickfan.com manga series"""
    pattern = r"https?://comickfan\.com/manga/([\w-]+)/?$"
    example = "https://comickfan.com/manga/the-demonic-supreme-sword"
    chapterclass = ComickfanChapterExtractor

    def chapters(self, page):
        slug = self.groups[0]
        url = f"{self.root}/api/comics/{slug}/chapter-list"
        params = {"per_page": 2000}

        data = self.request_json(url, params=params)

        results = []
        for ch in data.get("data", []):
            ch_num = ch["chapter"]
            hash_id = ch["hash_id"]
            ch_url = f"{self.root}/manga/{slug}/chapter-{ch_num}-{hash_id}"

            results.append((ch_url, {
                "manga_id"    : ch.get("comic_id"),
                "chapter_id"  : ch.get("id"),
                "chapter_hash": hash_id,
                "chapter"     : ch_num,
                "title"       : ch.get("title"),
                "lang"        : ch.get("language"),
            }))
        return results
