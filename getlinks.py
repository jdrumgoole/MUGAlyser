import re
import argparse
import requests

parser = argparse.ArgumentParser()
parser.add_argument("searchfor", nargs="*", default=("MongoDB", "MUG"), help="list of search strings, the first to be used in meetup.com, the rest to further filter results")
args = parser.parse_args()

r = requests.get("https://www.meetup.com/topics/"+args.searchfor[0]+"/all/")

links = re.findall('"((http|ftp)s?://.*?)"', r.text)
links_list = [i[0] for i in links]

invalid = ("find", "None", "api", "url", "about", "pro", "jobs", "apps", "meetup_api", "topics", "cities", "privacy", "terms", "cookie_policy", "facebook_account_tie", "fbconnectxd_ssl.html", "help")

with open("urls_"+args.searchfor[0]+"_exactmatch.txt", "w") as f_exact, open("urls_"+args.searchfor[0]+"_allresults.txt", "w") as f_all:
    for url in links_list:
        if re.match(r"https://www\.meetup\.com/(.*)/", url):
          if url.count('/') == 4:
              urlname = url.replace("https://www.meetup.com/", "").replace("/", "")
              if urlname not in invalid:
                    if any(w in urlname.lower() for w in map(str.lower, args.searchfor)):
                        f_exact.write(urlname + '\n')
                    f_all.write(urlname + '\n')

print("url names containing only search criteria stored in urls_"+args.searchfor[0]+"_exactmatch.txt")
print("url names for all related results stored in urls_"+args.searchfor[0]+"_allresults.txt")