from abc import ABC, abstractmethod


class Platform(ABC):
    def __init__(self, savepath, retry=5) -> None:
        self.savepath = savepath
        self.retry = retry

    @abstractmethod
    def build_vedio(self) -> list:
        pass

    @abstractmethod
    def build_playlist(self) -> list:
        pass

    def GetPageHtml(self, url):
        count = 0
        while count < self.retry:
            try:
                from selenium import webdriver
                from selenium.webdriver.chrome.options import Options

                options = Options()
                options.add_argument("--headless=new")
                driver = webdriver.Chrome(options=options)  # or webdriver.Firefox()
                driver.get(url)
                html_source = driver.page_source
                driver.quit()
                return html_source
            except Exception as e:
                count += 1
                print(e)
        return ""
