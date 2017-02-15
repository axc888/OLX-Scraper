import requests
from bs4 import BeautifulSoup
import time
#constants
url = "http://www.olx.ba/pretraga?"
kategorija = "kategorija=18"
vrsta = "vrsta=samoprodaja"
sacijenom = "sacijenom=sacijenom"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
stranica = 1
#olx.ba gets internal error (status code 500) after around 500 requests in a row. We need to pause for 10 seconds after each 400 elements
#links = []
file = open('links.txt', 'w')
s = requests.Session()
while True:
    url = url + kategorija + "&" + "stranica=" + str(stranica) + "&" + vrsta + "&" + sacijenom
    r = s.get(url, headers = headers)
    page_content = r.content.decode()
    soup = BeautifulSoup(page_content, "html.parser")
    articles = soup.find_all(class_="naslov")
    for link in articles:
        #links.append("%s\n" % link.a["href"])
        file.write("%s\n" % link.a["href"])
    stranica += 1
    if r.status_code != 200:
        r.close()
        s.close()
        r.cookies.clear()
        s.cookies.clear()
        del s
        del r
        time.sleep(10)
        s = requests.Session()
        stranica -= 1
    print(stranica)#, len(links), r.status_code, r.cookies)
file.close()
