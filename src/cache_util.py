import json
import os

from file import File
from utils import parse_url

cache_file = "filecache.json"


def load_cache():
    cache = []
    if os.path.exists(cache_file):
        fr = open(cache_file, "r")
        cache = json.load(fr) or []
        fr.close()
        cache = [File.from_json(json.loads(item)) for item in cache]
    return cache


def find_in_cache(cache, key):
    for entry in cache:
        if entry.source == key:
            return entry
    return None


def dump_cache(cache):
    fw = open(cache_file, "w")
    json.dump([str(item) for item in cache], fw)
    fw.close()
