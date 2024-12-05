import json
import os

from utils import find_generic_cdn_link


class File:
    def __init__(
        self,
        name,
        source,
        storage_path,
        done=False,
        tags=None,
        cdn_fetcher=find_generic_cdn_link,
        access_url=None,
        post_download=None,
    ):
        self.name = name
        self.source = source
        self.access_url = access_url
        self.done = done
        self.storage_path = storage_path
        self.tags = tags
        self.retry = 0
        self.post_download = post_download
        self.cdn_fetcher = cdn_fetcher

    def get_name(self):
        return self.name

    def get_source(self):
        return self.source

    def get_access_url(self):
        if self.cdn_fetcher and not self.access_url:
            cdn_link, response = self.cdn_fetcher(self.source)
            self.access_url = cdn_link

            web_filename, web_file_extension = os.path.splitext(
                response["webpage_url_basename"]
            )
            local_name, local_extension = os.path.splitext(self.name or "")
            self.name = (local_name or web_filename) + (
                local_extension or web_file_extension
            )
        if os.path.isdir(self.storage_path):
            self.storage_path = os.path.join(self.storage_path, self.name)
        return self.access_url or self.source

    def get_storage_path(self):
        return self.storage_path

    def get_tags(self):
        return self.tags

    def get_retry(self):
        return self.retry

    def increment_retry(self):
        self.retry = self.retry + 1

    def __str__(self) -> str:
        return str(self.to_json())

    def to_json(self):
        attribute = dict(self.__dict__)
        del attribute["cdn_fetcher"]
        del attribute["post_download"]
        return json.dumps(attribute)

    def get_done(self):
        return self.done

    def set_done(self, state: bool):
        self.done = state

    @staticmethod
    def from_json(data):
        return File(
            name=data["name"],
            source=data["source"],
            storage_path=data["storage_path"],
            tags=data["tags"],
            done=data["done"],
        )
