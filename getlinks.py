from urllib.request import urlopen
import re
import ssl
import argparse

ssl._create_default_https_context = ssl._create_unverified_context

parser = argparse.ArgumentParser()
parser.add_argument("searchfor")
args = parser.parse_args()

searchfor = args.searchfor.replace(" ","+")

website = urlopen("https://www.meetup.com/find/?allMeetups=false&keywords="+searchfor+ "&radius=Infinity&userFreeform=Dublin%2C+Ireland&mcId=z1017818&sort=recommended&eventFilter=mysugg")
html = website.read().decode()

links = re.findall('"((http|ftp)s?://.*?)"', html)
links_list = [i[0] for i in links]

invalid = ("find", "None", "api", "url", "about", "pro", "jobs", "apps", "meetup_api", "topics", "cities", "privacy", "terms", "cookie_policy", "facebook_account_tie", "fbconnectxd_ssl.html")

f = open("urls_"+searchfor+".txt", "w")

for url in links_list:
    if re.match(r"https://www\.meetup\.com/(.*)/", url):
        if url.count('/') == 4:
            url = url.replace("https://www.meetup.com/", "").replace("/", "")
            if url not in invalid:
                f.write(url + '\n')
                continue
    else:
        links_list.remove(url)

print("url names stored in urls_"+searchfor+".txt")


