import time
import re
import unicodedata
import re
import sys
import requests
import os


def parse_url(url):
    if sys.version_info.major == 3:
        from urllib.parse import urlparse, parse_qs, urljoin
    else:
        from urlparse import urlparse, parse_qs, urljoin
    u = urlparse(url)
    return {
        "url": urljoin(url, u.path),
        "query": parse_qs(u.query),
        "domain": (u.scheme + "://" if u.scheme else "") + u.hostname,
        "hostname": u.hostname,
    }


def sanitize_filename(value, allow_unicode=False):
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")[0:100]


def find_generic_cdn_link(url):
    def get_url(baseUrl):
        webUrl = "https://en.fetchfile.net/fetch/"
        payload = {"url": baseUrl, "action": "homePure"}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": parse_url(baseUrl)["hostname"],
        }
        stopper = False
        startTime = time.time()
        while not stopper:
            response = requests.post(webUrl, data=payload, headers=headers)
            responseJson = response.json()
            if "url" in responseJson:
                stopper = True
            else:
                time.sleep(3)
            currentTime = time.time()
            if (currentTime - startTime) > 200:
                raise Exception({"msg": "Link not resolved", "extrasInfo": baseUrl})
        return responseJson["url"], responseJson

    cdn_url = None
    response = None
    while True:
        cdn_url, response = get_url(url)
        if cdn_url == url:
            break
        url = cdn_url
    return cdn_url, response


def cleanup(dir):
    d = [os.path.join(dir, f) for f in os.listdir(dir)]
    d = [f for f in d if os.path.isfile(f)]
    cap = 2 * 1024 * 1024
    for f in d:
        _, file_extension = os.path.splitext(f)
        try:
            if file_extension.endswith("temp"):
                os.remove(f)
        except:
            pass


def load_file_link(filename):
    fr = open(filename, "r")
    lines = [line.replace("\n", "") for line in fr.readlines() if line]
    lines = [line for line in lines if line]
    fr.close()
    return lines