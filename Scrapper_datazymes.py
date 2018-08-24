from bs4 import BeautifulSoup
import requests
import re
import json
from elasticsearch import Elasticsearch

es=Elasticsearch()
count=1
def qoutput(response):
    ctr=0
    keys = []
    values = []
    for i in response:
        j = str(i)
        x = j.find(',')
        j = j[0:x]
        y = j.find(':')
        ans = j[y:x - 1]
        z = ans.find("'")
        ans = ans[z + 1:x - 1]
        keys.insert(ctr,str(ans.strip()))
        ctr=ctr+1
    ctr = 0
    for i in response:
        j = str(i)
        x = j.find(',')
        j = j[x:len(j)]
        y = j.find(':')
        values.insert(ctr,str(j[y + 1:len(j) - 1].strip()))
        ctr=ctr+1

    return ourzip(keys,values)


def ourzip(k,v):
    a=""
    a=k[0]+"   "+v[0]
    for q in range(1,len(k)):
        a=a+","+k[q]+"   "+v[q]
    return a



def search(doc):
    global count
    response=es.index(index='doctor', doc_type='info', id=count, body=doc)
    #print response
    count=count+1
    return


## Extracting zip code
def zip(location):
    y = location[len(location) - 5:len(location)]
    return y



## Extracting location
def stl(location):
        y = ""
        t = ""
        op=[]

        for x in ((str(location.text.strip()))):
            if x.isalnum() | ((x == " ") & (t != " ")):
                t = x
                y = y + x
        return y



### Formatting the education and certificates
def stext(line):
    y = ""
    t = ""
    n = ""
    for x in ((str(line))):
        if (x == "\\") | (n == "flag"):
            if (n == "flag"):
                n = "not"
                y = y + " "
                continue
            else:
                n = "flag"
                continue
        if x.isalnum() | ((x == " ") & (t != " ")):
                t = x
                y = y + x
    return y




#### Extracting doctor information


def extractdoctdetail(url,city):
    url = "https://health.usnews.com"+url
    src = requests.get(url, headers=headers1).text
    soup = BeautifulSoup(src, 'html.parser')
    try:
        name = soup.find("h1", attrs={"class": "hero-heading flex-media-heading block-tight doctor-name "})
        name = name.contents
        name = str(name[0]).strip()
        overview = soup.find("div", attrs={"class": "block-normal clearfix"})
        overview = str(overview.text.strip())
        #print overview
        yp = soup.findAll("span", attrs={"class": "text-large heading-normal-for-small-only right-for-medium-up"})
        yp = str(yp[1].text.strip())
        if (yp)=="Male":
           yp = None
        elif (yp) == "Female":
            yp = None
        #print yp
        lk = soup.findAll("span", attrs={
            "class": "text-large heading-normal-for-small-only right-for-medium-up text-right showmore"})
        lk = str(lk[0].text.strip())
        #print lk
        location = soup.findAll("span", attrs={"class": "text-strong"})
        location = location[1]
        location=stl(location)
        #print location
        z=zip(location)
        #print z

        try:
            affl = soup.findAll("a", attrs={"class": "heading-larger block-tight"})
            for child in affl:
                print child.text.strip()
        except:
            affl = "Not Mensioned"
            #print affl
        spec = soup.find("a", attrs={"class": "text-large"})
        spec = str(spec.text.strip())
        subspec = soup.find("p", attrs={"class": "text-large block-tight"})
        subspec = str(subspec.text.strip())
        edu = soup.findAll("section", attrs={"class": "block-loosest"})
        c=5
        if len(edu[5].findChildren("ul", recursive=False))==0:
            c+=1
            edu = edu[c].findChildren("ul", recursive=False)
            edu = edu[0].findChildren("li", recursive=True)
        else:
            edu = edu[c].findChildren("ul", recursive=False)
            edu = edu[0].findChildren("li", recursive=True)
        c=c+1
        i = 0
        edutext = []
        for child in edu:
            edutext.insert(i, str(child.text.strip()).strip())
            i = i + 1
        edx=stext(edutext)
        #print edx
        edu = soup.findAll("section", attrs={"class": "block-loosest"})
        cert = edu[c].findChildren("ul", recursive=False)
        cert = cert[0].findChildren("li", recursive=True)
        i = 0
        certtext = []
        for child in cert:
            certtext.insert(i, str(child.text.strip()).strip())
            i = i + 1
        ct=stext(certtext)
        #print ct
        doc={
            "spec":spec,
             "city":city,
              "zip":z,
              "yp":yp
        }
        search(doc)
    except:
        edutext="Not Mensioned"
        certtext="Not Mensioned"
    return;







### Extracting doctros under speciality
def doctorextract(url,city):
    print "doctors in the city"
    src = requests.get(url, headers=headers1).text
    soup = BeautifulSoup(src, 'html.parser')
    for link in soup.findAll('a', attrs={'href': re.compile("/doctors/"), "class": "search-result-link bar-tighter"}):
        extractdoctdetail(link.get('href'),city)
        print link.get('href')
    return;








### Main code
headers1 = {"User-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"}
url = 'https://health.usnews.com/doctors/city-index/new-jersey'
src = requests.get(url, headers=headers1).text
soup = BeautifulSoup(src, 'html.parser')
city_name = soup.findAll("li", attrs={"class": "List__ListItem-dl3d8e-1 kfaWAY"})

#### Extracting the city
list = []
i = 0
for a in city_name:
    list.insert(i, a.text.strip())
    i = i + 1


#### Extracting the speciality
for l in list[0:3]:
    print l
    spec_url = "https://health.usnews.com/doctors/specialists-index/new-jersey"
    updated_url = spec_url + "/" + str(l).lower()
    #print(updated_url)
    request = requests.get(updated_url, headers=headers1).text
    soup = BeautifulSoup(request, "html.parser")
    spec_name = soup.findAll("li", attrs={"class": "List__ListItem-dl3d8e-1 kfaWAY"})
    for ab in spec_name[0:3]:
        print ab.text.strip() + "in" +" "+l
        url = "https://health.usnews.com/" + str(ab.a.get("href"))
        print url
        doctorextract(url,l)
print "Exit"
response = es.search(
        index="doctor",
        body={
            "aggs": {
                "genres": {
                    "terms": {"field": "city.keyword"}
                }
            }
        }
    )
#print response
response = response['aggregations']['genres']['buckets']
resultc=qoutput(response)
print resultc
response = es.search(
        index="doctor",
        body={
            "aggs": {
                "genres": {
                    "terms": {"field": "spec.keyword"}
                }
            }
        }
    )
response = response['aggregations']['genres']['buckets']
results=qoutput(response)
print results
response = es.search(
        index="doctor",
        body={
            "aggs": {
                "genres": {
                    "terms": {"field": "zip.keyword"}
                }
            }
        }
    )
response = response['aggregations']['genres']['buckets']
resultz=qoutput(response)
print resultz
response = es.search(
        index="doctor",
        body={
            "aggs": {
                "genres": {
                    "terms": {"field": "yp.keyword"}
                }
            }
        }
    )
response = response['aggregations']['genres']['buckets']
resultyp=qoutput(response)
print resultyp
finalout={
    "city":resultc,
    "spec":results,
    "yp":resultyp,
    "zip":resultz
}
with open("./analysis_ques.json","w") as write_file:
    json.dump(finalout,write_file)
