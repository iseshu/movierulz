import requests
from flask import *
from flask_cors import CORS
from bs4 import BeautifulSoup


app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

def scape_link(url:str)->str:
    req = requests.get(url).content
    soup = BeautifulSoup(req,"html.parser")
    link = soup.find("a",{"class":"main-button dlbutton"})['href']
    return link 


def get_page(url:str)->list:
    req = requests.get(url).content
    soup = BeautifulSoup(req,"html.parser")
    print(soup)
    divs = soup.find_all("div",class_="cont_display")
    data = []
    for i in range(2,len(divs)):
        title = divs[i].find("a")
        img = divs[i].find("img")
        dat = {"title":title['title'],"image":img['src'],"link":title['href']}
        data.append(dat)
    return data
def get_movie(url:str)->dict:
    req = requests.get(url).content
    soup = BeautifulSoup(req,"html.parser")
    title = soup.find("h2",class_="entry-title").text.replace("Full Movie Watch Online Free","")
    image = soup.find("img",class_="attachment-post-thumbnail size-post-thumbnail wp-post-image")['src']
    description = soup.find_all("p")[4].text
    torrents = soup.find_all("a",class_="mv_button_css")
    torrent = []
    other_links = []
    for tor in torrents:
        link = tor['href']
        size = tor.find_all("small")[0].text
        quality = tor.find_all("small")[1].text
        data = {"magnet":link,"size":size,"quality":quality}
        torrent.append(data)
    ps = soup.find_all("p")
    for p in ps:
        if p.find("strong"):
            if "Watch Online –" in p.find("strong").text:
                typ = p.find("strong").text.split("–")[-1]
                
                try:
                    lin = p.find("a")['href']
                    data = {"type":typ,"url":lin}
                    other_links.append(data)
                except:
                    pass
    data = {"status":True,"url":url,"title":title,"description":description,"image":image,"torrent":torrent,"other_links":other_links}
    return data


@app.route("/search",methods=["GET"])
def search():
    a = request.args.get("query")
    url = f"https://www.5movierulz.phd/?s={a}"
    try:
        data = get_page(url)
        total = len(data)
        main_data = {"status":True,"total_found":total,"url":url,"data":data}
    except:
        main_data = main_data = {"status":False,"msg":"No Data Found"}
    return jsonify(main_data)

@app.route("/<language>/<page>")
def get_home(language:str,page:int):
    page = 1 if page == None else page
    if language == "telugu":
        url = "https://www.5movierulz.phd/telugu-movie/page/"+str(page)
    elif language == "hindi":
        url = "https://www.5movierulz.phd/bollywood-movie-free/page/"+str(page)
    elif language == "tamil":
        url = "https://www.5movierulz.phd/tamil-movie-free/page/"+str(page)
    elif language == "malayalam":
        url = "https://www.5movierulz.phd/malayalam-movie-online/page/"+str(page)
    elif language == "english":
        url = "https://www.5movierulz.phd/category/hollywood-movie-2023/"
    else:
        url = None
    if url != None:
        data = get_page(url)
        total = len(data)
        main_data = {"status":True,"total_found":total,"url":url,"data":data}
    else:
        main_data = {"status":False}
    return jsonify(main_data)

@app.route("/")
def home():
    url = "https://www.5movierulz.phd/"
    data = get_page(url)
    total = len(data)
    main_data = {"status":True,"total_found":total,"url":url,"data":data}
    return jsonify(main_data)

@app.route("/fetch",methods=["GET"])
def s():
    a = request.args.get("url")
    req = requests.get(a)
    return req.content

@app.route("/get",methods=["GET"])
def get_s():
    a = request.args.get("url")
    try:
        data = get_movie(a)
        return jsonify(data)
    except Exception as e:
        data = {"status":False,"msg":"Unable to get data","error":e}
        return jsonify(data)

@app.route("/ip")
def getip():
    return requests.get("https://www.5movierulz.phd").text


if __name__ == "__main__":
    app.run()
