import re
import requests


class LinkHandler:
    def __init__(self):
        self.link_pattern = re.compile(
            r"""
            https?:\/\/
            (?:www\.)?
            (?:
                instagram\.com\/(?:reel|p)\/[\w-]+\/?(?:\?[^\s]*)? |
                tiktok\.com\/@[\w.-]+\/(?:video|photo)\/\d+ |
                tiktok\.com\/embed(?:\/v2)?\/\d+ |
                vm\.tiktok\.com\/[\w\/]+ |
                vt\.tiktok\.com\/[\w\/]+
            )
            \/?
            (?:\?[^\s]*)?
            """,
            re.VERBOSE,
        )
        self.shortcode_pattern = re.compile(
            r"""
            (?:https?:\/\/(?:www\.)?)
            (?:
                instagram\.com\/(?:reel|p)\/(?P<instagram_shortcode>[\w-]+) |
                v[mt]\.tiktok\.com\/(?P<tiktok_shortcode_short>[^\/\?\s]+) |
                tiktok\.com\/@[\w.-]+\/video\/(?P<tiktok_shortcode_long>\d+)
            )
            """,
            re.VERBOSE,
        )
        self.tiktok_type_pattern = re.compile(r"tiktok\.com/@[\w.-]*/(video|photo)/\d+")

    def extract_shortcode(self, url):
        match = self.shortcode_pattern.search(url)
        if not match:
            return None

        return next(
            (group for group in match.groupdict().values() if group is not None), None
        )

    def _resolve_tiktok_link(self, url):
        try:
            response = requests.get(url, allow_redirects=True, timeout=5)
            return response.url
        except Exception as e:
            raise ValueError(f"Failed to resolve TikTok link: {e}")

    def extract_tiktok_type(self, url):
        resolved = self._resolve_tiktok_link(url)
        match = self.tiktok_type_pattern.search(resolved)
        if match:
            return match.group(1)
        raise ValueError("Type not found in resolved TikTok URL")
