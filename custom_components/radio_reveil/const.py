"""Constants for Radio Réveil integration."""

DOMAIN = "radio_reveil"
VERSION = "1.0.0"

# Config entry keys
CONF_MEDIA_PLAYER = "media_player"
CONF_VOLUME = "volume"
CONF_RADIO_URL = "radio_url"

DAYS_FR = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
DAYS_FR_FULL = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
DAYS_HA = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

CONF_DAY_ENABLED = "enabled"
CONF_DAY_TIME = "time"

DEFAULT_VOLUME = 0.5
DEFAULT_TIMES = ["07:00", "07:00", "07:00", "07:00", "07:00", "08:30", "08:30"]
DEFAULT_ENABLED = [True, True, True, True, True, False, False]

RADIOS: list[dict] = [
    {"label": "Mouv'",           "url": "http://icecast.radiofrance.fr/mouv-hifi.aac"},
    {"label": "FIP",             "url": "http://icecast.radiofrance.fr/fip-midfi.mp3"},
    {"label": "France Inter",    "url": "http://icecast.radiofrance.fr/franceinter-midfi.mp3"},
    {"label": "France Info",     "url": "http://icecast.radiofrance.fr/franceinfo-midfi.mp3"},
    {"label": "France Musique",  "url": "http://icecast.radiofrance.fr/francemusique-midfi.mp3"},
    {"label": "Skyrock",         "url": "http://icecast.skyrock.net/s/natio_mp3_128k"},
    {"label": "NRJ",             "url": "https://streaming.nrjaudio.fm/oumvmk8fnozc?origine=fluxurlradio"},
    {"label": "Rire & Chansons", "url": "https://streaming.nrjaudio.fm/ou8o8xgk7oiu?origine=fluxurlradio"},
    {"label": "OUI FM",          "url": "https://ouifm.ice.infomaniak.ch/ouifm-high.mp3"},
    {"label": "Fun Radio",       "url": "https://cdn.nrjaudio.fm/adwz1/fr/30015/mp3_128.mp3"},
    {"label": "RFI Monde",       "url": "https://stream.rfi.fr/rfi-monde-64.mp3"},
    {"label": "BBC Radio 4",     "url": "https://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio4_mf_p"},
    {"label": "BBC World",       "url": "http://a.files.bbci.co.uk/media/live/manifesto/audio/simulcast/hls/nonuk/sbr_low/ak/bbc_world_service.m3u8"},
]

RADIO_LABELS = [r["label"] for r in RADIOS]
RADIO_URL_MAP = {r["label"]: r["url"] for r in RADIOS}

PLATFORMS = ["switch", "select", "number", "text", "time"]
