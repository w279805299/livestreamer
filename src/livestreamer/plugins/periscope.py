import re

from livestreamer.plugin import Plugin
from livestreamer.plugin.api import http, validate
from livestreamer.stream import HLSStream


STREAM_INFO_URL = "https://api.periscope.tv/api/v2/getAccessPublic"

STATUS_GONE = 410
STATUS_UNAVAILABLE = (STATUS_GONE,)

_url_re = re.compile(r"http(s)?://(www\.)?periscope.tv/w/(?P<broadcast_id>[\w\-\=]+)")
_stream_schema = validate.Schema(
    {"hls_url": validate.url(scheme="http")},
    validate.get("hls_url")
)


class Periscope(Plugin):
    @classmethod
    def can_handle_url(cls, url):
        return _url_re.match(url)

    def _get_streams(self):
        match = _url_re.match(self.url)
        res = http.get(STREAM_INFO_URL,
                       params=match.groupdict(),
                       acceptable_status=STATUS_UNAVAILABLE)

        if res.status_code in STATUS_UNAVAILABLE:
            return

        playlist_url = http.json(res, schema=_stream_schema)
        return HLSStream.parse_variant_playlist(self.session, playlist_url)


__plugin__ = Periscope
