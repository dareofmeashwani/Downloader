from platforms.platform import Platform
from file import File
from utils import parse_url, sanitize_filename
from cache_util import dump_cache, find_in_cache, load_cache
import hashlib
from bs4 import BeautifulSoup


class Default(Platform):
    def __init__(self, savepath, retry=5) -> None:
        super().__init__(savepath, retry)

    def linkFilter(self, aTag):
        return aTag.has_attr("class") and aTag["class"] == ["js-pop"]

    def fetch_urls(self, seed, filterCallback=None, pageSize=30, pageType="grid"):
        domain = parse_url(seed)["domain"]
        #seedBackName = str(hashlib.sha1(seed.encode()).hexdigest()) + ".backup"
        urlMap = {}
        stopper = False
        while not stopper:
            data = self.GetPageHtml(seed)
            soup = BeautifulSoup(data, "html.parser")
            linkCount = 0
            for aTag in soup.findAll("a"):
                if self.linkFilter(aTag):
                    if filterCallback:
                        if (
                            filterCallback(aTag)
                            and aTag.has_attr("href")
                            and aTag["href"] not in urlMap
                        ):
                            urlMap[aTag["href"]] = True
                            linkCount = linkCount + 1
                    elif aTag.has_attr("href") and aTag["href"] not in urlMap:
                        urlMap[aTag["href"]] = True
                        linkCount = linkCount + 1
            if linkCount == 0:
                stopper = True
            seed = self.find_next_page(seed, pageSize, pageType)
        urls = [domain + l for l in list(urlMap.keys())]
        return urls

    def find_vedio_title(self, baseUrl):
        data = self.GetPageHtml(baseUrl)
        soup = BeautifulSoup(data, "html.parser")
        title = soup.find("title")
        return title.text

    def find_next_page(self, url, pageSize=20, pageType="grid"):
        if pageType == "grid":
            parsedUrl = parse_url(url)
            return (
                parsedUrl["url"]
                + "?page="
                + str(
                    (
                        parsedUrl["query"]
                        and parsedUrl["query"]["page"]
                        and int(parsedUrl["query"]["page"][0])
                        or 0
                    )
                    + pageSize
                )
            )
        else:
            pass

    def build_playlist(self, source):
        return self.build_vedio(self.fetch_urls(source))

    def build_vedio(self, links):

        cache = load_cache()

        temp_list = [links] if isinstance(links, str) else links
        return_list = []
        for link in temp_list:
            link = parse_url(link)['url']
            entry = find_in_cache(cache, link)
            if entry:
                return_list.append(entry)
            else:
                entry = File(
                    name=sanitize_filename(self.find_vedio_title(link)),
                    source=link,
                    storage_path=self.savepath,
                )
                return_list.append(entry)
                cache.append(entry)

        dump_cache(cache)

        return return_list
