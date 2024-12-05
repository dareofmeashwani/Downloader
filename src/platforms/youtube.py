from cache_util import dump_cache, find_in_cache, load_cache
from file import File
from platforms.platform import Platform
from utils import find_generic_cdn_link, sanitize_filename


class Youtube(Platform):
    def __init__(self, savepath, retry=5) -> None:
        super().__init__(savepath, retry)

    def build_vedio(self, links):
        #cache = load_cache()
        temp_list = [links] if isinstance(links, str) else links
        return_list = []
        for link in temp_list:
            #entry = find_in_cache(cache, link)
            entry = None
            if not entry:
                response = self.find_youtube_cdn_link(link)
                '''
                entry = File(
                    name="hello",
                    source=link,
                    storage_path=self.savepath,
                    post_download=self.combine_vedio_audio
                )
                #return_list.append(entry)
                #cache.append(entry)
                '''

        #dump_cache(cache)

        return return_list
    def build_playlist(self, link) -> list:
        pass
    
    def combine_vedio_audio():
        pass
    
    def find_youtube_cdn_link():
        return