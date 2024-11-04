from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
main_url = "https://cf-proxy.seshu-yarra.workers.dev"
def scape_link(url: str) -> str:
    req = requests.get(url).content
    soup = BeautifulSoup(req, "html.parser")
    link = soup.find("a", {"class": "main-button dlbutton"})['href']
    return link

def get_page(url: str) -> list:
    req = requests.get(url).content
    soup = BeautifulSoup(req, "html.parser")
    divs = soup.find_all("div", class_="cont_display")
    data = []
    for i in range(2, len(divs)):
        title = divs[i].find("a")
        img = divs[i].find("img")
        dat = {"title": title['title'], "image": img['src'], "link": title['href']}
        data.append(dat)
    return data

def get_movie(url: str) -> dict:
    req = requests.get(url).content
    soup = BeautifulSoup(req, "html.parser")
    title = soup.find("h2", class_="entry-title").text.replace("Full Movie Watch Online Free", "")
    image = soup.find("img", class_="attachment-post-thumbnail size-post-thumbnail wp-post-image")['src']
    description = soup.find_all("p")[4].text
    torrents = soup.find_all("a", class_="mv_button_css")
    torrent = []
    other_links = []
    for tor in torrents:
        link = tor['href']
        size = tor.find_all("small")[0].text
        quality = tor.find_all("small")[1].text
        data = {"magnet": link, "size": size, "quality": quality}
        torrent.append(data)
    ps = soup.find_all("p")
    for p in ps:
        if p.find("strong"):
            if "Watch Online –" in p.find("strong").text:
                typ = p.find("strong").text.split("–")[-1]
                try:
                    lin = p.find("a")['href']
                    data = {"type": typ, "url": lin}
                    other_links.append(data)
                except:
                    pass
    data = {"status": True, "url": url, "title": title, "description": description, "image": image, "torrent": torrent, "other_links": other_links}
    return data

@app.get("/search")
async def search(query: str):
    url = main_url+f"/?s={query}"
    try:
        data = get_page(url)
        total = len(data)
        main_data = {"status": True, "total_found": total, "url": url, "data": data}
    except:
        main_data = {"status": False, "msg": "No Data Found"}
    return JSONResponse(content=main_data)

@app.get("/{language}/{page}")
async def get_home(language: str, page: int = 1):
    if language == "telugu":
        url = main_url+f"/telugu-movie/page/{page}"
    elif language == "hindi":
        url = main_url+f"/bollywood-movie-free/page/{page}"
    elif language == "tamil":
        url = main_url+f"/tamil-movie-free/page/{page}"
    elif language == "malayalam":
        url = main_url+f"/malayalam-movie-online/page/{page}"
    elif language == "english":
        url = main_url+"/category/hollywood-movie-2023/"
    else:
        url = None
    if url:
        data = get_page(url)
        total = len(data)
        main_data = {"status": True, "total_found": total, "url": url, "data": data}
    else:
        main_data = {"status": False}
    return JSONResponse(content=main_data)

@app.get("/")
async def home():
    url = main_url+"/"
    data = get_page(url)
    total = len(data)
    main_data = {"status": True, "total_found": total, "url": url, "data": data}
    return JSONResponse(content=main_data)

@app.get("/fetch")
async def fetch(url: str):
    req = requests.get(url)
    return req.content

@app.get("/get")
async def get_s(url: str):
    try:
        data = get_movie(url)
        return JSONResponse(content=data)
    except Exception as e:
        data = {"status": False, "msg": "Unable to get data", "error": str(e)}
        return JSONResponse(content=data)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
