import requests
from bs4 import BeautifulSoup
import csv
import codecs

file_txt = open("links2.txt", "r")
urls = file_txt.readlines()
file_txt.close()
print(len(urls))
file_csv = open("data.csv", "w", newline='')
csv_writer = csv.writer(file_csv)
csv_writer.writerow(['Link','Cijena', 'Stanje', 'Lokacija', 'Proizvodjac', 'Model', 'Godiste', 'Kilometraza', 'Emisija'])

browser_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
lista = []
for url in urls:
    r = requests.get(url.replace("\n",""), headers = browser_headers)
    page_content = r.content.decode()

    soup = BeautifulSoup(page_content, "html.parser")
    try: #just skip all exceptions :)
        cijena = soup.find(class_="op pop mobile-cijena ").find("p").find_next("p").get_text().replace("KM","").replace(".","").strip()
        stanje = soup.find(class_="op mobile-stanje").find("p").find_next("p").get_text().strip()
        lokacija = soup.find(class_="op pop mobile-lokacija").find("p").find_next("p").get_text().strip().replace("\u0107","c").replace("\u010d","c").replace("\u010c","c")
        proizvodjac = soup.find(class_="op pop ispod").find("p").find_next("p").get_text().strip()
        model = soup.find(class_="op ispod").find("p").find_next("p").get_text().strip()
        godiste = soup.find(class_="op ispod").find_next(class_="op ispod").find("p").find_next("p").get_text().strip()
        kilometraza_tag = soup.find(class_="op ispod").find_next(class_="op ispod").find_next(class_="op ispod").find("p").get_text().replace(".", "").strip()
        if kilometraza_tag == "Gorivo":
            kilometraza = "NaN"
        else:
            kilometraza = soup.find(class_="op ispod").find_next(class_="op ispod").find_next(class_="op ispod").find("p").find_next("p").get_text().replace(".","").strip()
        #this try/except block is less expensive than using if
        try:
            emisija = soup.find('div', id = 'dodatnapolja1').find('div', text= 'Emisioni standard').find_next('div').text
        except:
            emisija = "NaN"
        #if soup.find('div', id = 'dodatnapolja1').find('div', text= 'Emisioni standard').find_next('div').text is not None:
            #emisija = soup.find('div', id = 'dodatnapolja1').find('div', text= 'Emisioni standard').find_next('div').text
        lista.append([cijena, stanje, lokacija, proizvodjac, model, godiste, kilometraza, emisija])
    except:
        pass #:)

    csv_writer.writerow([url, cijena, stanje, lokacija, proizvodjac, model, godiste, kilometraza, emisija])

    print(len(lista),lista[-1])
