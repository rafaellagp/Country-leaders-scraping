import requests
from bs4 import BeautifulSoup
import re
import functools
import json

cache = {}
def hashable_cache(f):
    def inner(url, session):
        if url not in cache:
            cache[url] = f(url, session)
        return cache[url]
    return inner

s = requests.Session()
@hashable_cache
def get_first_paragraph(wikipedia_url, s):
    req = requests.get(wikipedia_url)
    soup = bs4.BeautifulSoup(req.text, "html.parser")
    for paragraph in soup.find_all('p'):
        if paragraph.find_all('b'):
            re.sub(r".\[.\]", ",", paragraph.text)
            text = paragraph.text
            regex1 = r".\[.\]"
            paragraph_correct = re.sub(regex1, "", text)
            regex2 = r"\("
            paragraph_correct = re.sub(regex2, ", ", paragraph_correct)
            regex3 = r"\)"
            paragraph_correct = re.sub(regex3, " ", paragraph_correct)
    return paragraph_correct

def get_leaders():
    root_url = 'https://country-leaders.herokuapp.com'
    
    cookie_url = root_url + '/cookie'
    cookies = s.get(cookie_url).cookies
    
    countries_url = root_url + '/countries'
    req_country = s.get(countries_url, cookies=cookies)
    countries = req_country.json()
    
    leaders_url = root_url + '/leaders'
    leaders_per_country = {}

    for country in countries:
        params = {'country': country}
        req_leaders = s.get(leaders_url, params = params, cookies=cookies)
        
        if req_leaders.status_code == 403:
                cookies = s.get(cookie_url).cookies
                req_leaders = s.get(leaders_url, params=params, cookies=cookies)
                
        leaders = req_leaders.json()
        
        for leader in leaders:
            leader["first_paragraph"] = get_first_paragraph(leader["wikipedia_url"],s)
        leaders_per_country[country] = leaders
        
    return leaders_per_country

get_leaders()

leaders_per_country = get_leaders()

def save():
    filename = "leaders.json"
    json.dump(leaders_per_country, open(filename, "w"))
save()
