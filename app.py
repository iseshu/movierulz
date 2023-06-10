import re
import requests
from flask import *
from flask_cors import CORS
from bs4 import BeautifulSoup


app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})


def get_page(url):
    req = requests.get(url).content
    soup = BeautifulSoup(req,"html.parser")
    divs = soup.find_all("div",class_="cont_display")
    data = []
    for i in range(2,len(divs)):
        title = divs[i].find("a")
        img = divs[i].find("img")
        dat = {"title":title['title'],"image":img['src'],"link":title['href']}
        data.append(dat)
    return data

import re
import requests
from bs4 import BeautifulSoup
def get_movie(url):
    req = requests.get(url).content
    soup = BeautifulSoup(req,"html.parser")
    title = soup.find("h2",class_="entry-title").text.replace("Full Movie Watch Online Free","")
    image = soup.find("img",class_="attachment-post-thumbnail size-post-thumbnail wp-post-image")['src']
    description = soup.find_all("p")[4].text
    torrents = soup.find_all("a",class_="mv_button_css")
    pre_tag = soup.find("pre")
    screenshots = re.findall(r'https?://[^\s]+', pre_tag.text)
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
                if "all" in typ.lower():
                    lin = p.find("a")['href']
                    req = requests.get(lin).text
                    soup = BeautifulSoup(req,'html.parser')
                    div = soup.find("div",class_="entry-content wp-block-post-content has-global-padding is-layout-constrained")
                    p_s = div.find_all("p")
                    for op in p_s:
                        if op.find("strong") and op.find("a"):
                            lin = op.find("a")['href']
                            typ = op.find("strong").text.split("–")[-1]
                            other_links.append(data)
                else:
                    lin = p.find("a")['href']
                    data = {"type":typ,"url":lin}
                    other_links.append(data)
    data = {"status":True,"url":url,"title":title,"description":description,"screenshots":screenshots,"image":image,"torrent":torrent,"other_links":other_links}
    return data



@app.route("/search",methods=["GET"])
def search():
    a = request.args.get("query")
    url = f"https://ww2.5movierulz.wf/?s={a}"
    try:
        data = get_page(url)
        total = len(data)
        main_data = {"status":True,"total_found":total,"url":url,"data":data}
    except:
        main_data = main_data = {"status":False,"msg":"No Data Found"}
    return jsonify(main_data)

@app.route("/<language>")
def get_home(language):
    if language == "telugu":
        url = "https://ww2.5movierulz.wf/telugu-movie/"
    elif language == "hindi":
        url = "https://ww2.5movierulz.wf/bollywood-movie-free/"
    elif language == "tamil":
        url = "https://ww2.5movierulz.wf/tamil-movie-free/"
    elif language == "malayalam":
        url = "https://ww2.5movierulz.wf/malayalam-movie-online/"
    elif language == "english":
        url = "https://ww2.5movierulz.wf/category/hollywood-movie-2021/"
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
    url = "https://ww2.5movierulz.wf/"
    data = get_page(url)
    total = len(data)
    main_data = {"status":True,"total_found":total,"url":url,"data":data}
    return jsonify(main_data)

@app.route("/get",methods=["GET"])
def get_s():
    a = request.args.get("url")
    try:
        data = get_movie(a)
        return jsonify(data)
    except:
        data = {"status":False,"msg":"Unable to get data"}
        return jsonify(data)

if __name__ == "__main__":
    app.run()
