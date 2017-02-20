import requests
from queue import Queue
from bs4 import BeautifulSoup
from time import sleep
import sys
import pandas as pd


class OLXScraper(object):
    def __init__(self, category=18, from_page=1, to_page=5000, links_file=True, data_file=True, no_of_threads=1):
        """
        OLX Scraper needs some initial attributes to work:
        :param category: integer that represents the category(e.g. category 18 are cars)
        :param from_page: integer that shows the starting page that will be scraped
        :param to_page: integer that shows ending page to be scraped (it is inclusive)
        :param links_file: boolean value that creates a file with all links that are scraped, if links_file is True
        :param data_file: boolean value that creates a main file with all the data, if data_file is True
        """

        self.links = Queue(maxsize=0)
        self.main_list = Queue(maxsize=0)
        self.urls = Queue(maxsize=0)

        self.category = category
        self.from_page = from_page
        self.to_page = to_page
        self.links_file = links_file
        self.data_file = data_file

        while from_page < to_page:
            self.urls.put("http://www.olx.ba/pretraga?kategorija=" + str(category) + "&stranica=" + str(from_page))
            from_page += 1

    def link_scraper(self):
        from_page = self.from_page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
        if self.links_file:
            links_file = open("links2.txt", "w")

        print("Number of pages: " + str(self.urls.qsize()))
        while not self.urls.empty():
            try:
                r = requests.get(self.urls.get(), headers=headers)
                r.raise_for_status()
                page_content = r.content.decode()
                soup = BeautifulSoup(page_content, "lxml")
                articles = soup.find_all(class_="naslov")
                if len(articles) == 0:
                    print("Stopped scraping at page: " + str(from_page))
                    return self.links
                for link in articles:
                    self.links.put(link.a["href"])
                    if self.links_file:
                        links_file.write("%s\n" % link.a["href"])
                print(self.links.qsize())
            except:
                sleep(3)
                print("Zasp'o sam sekund... kriv je " + str(r.status_code))
            self.urls.task_done()
        return self.links

    def page_scraper(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
        while not self.links.empty():
            attributes = {}
            main_items = {}
            items = {}
            url = self.links.get()
            try:
                r = requests.get(url, headers=headers)
                r.raise_for_status()
            except:
                print("Error: ", sys.exc_info()[0], "  Status code: " + str(r.status_code))
                sleep(3)
                r = requests.get(url, headers=headers)
            page_content = r.content.decode()
            soup = BeautifulSoup(page_content, "lxml")

            main_attrs = soup.find_all('p', {'class': 'n'})
            main_attrs_keys = []
            main_attrs_values = []
            for attr in main_attrs:
                main_attrs_keys.append(attr.get_text().strip())
            for attr in main_attrs:
                main_attrs_values.append(attr.find_next('p').get_text().strip())
            main_items = dict(zip(main_attrs_keys, main_attrs_values))

            df1_list = []
            df2_list = []
            df1 = soup.find_all('div', {'class': 'df1'})
            df2 = soup.find_all('div', {'class': 'df2'})
            for df in df1:
                df1_list.append(df.get_text().strip())
            for df in df2:
                df2_list.append('1' if df.get_text().strip() == '' else df.get_text().strip())
            items = dict(zip(df1_list, df2_list))

            attributes = {**main_items, **items}
            self.main_list.put(attributes)
            print(self.main_list.qsize())
            self.links.task_done()

        single_list = list(self.main_list.queue)
        df = pd.DataFrame(single_list)
        if self.data_file:
            df.to_csv("data2.csv", encoding="utf-8", na_rep="NaN", index=False)
        return df

scraper = OLXScraper(category=18,from_page=1,to_page=6)
links = scraper.link_scraper()
scraper.page_scraper()
