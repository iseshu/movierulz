from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import cloudscraper
from bs4 import BeautifulSoup
import re
requests = cloudscraper.create_scraper()
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
    title = soup.find("h2", class_="entry-title").get_text(strip=True)
    title = title.replace("Full Movie Watch Online Free", "").strip()
    image = soup.find("img", class_="attachment-post-thumbnail")["src"]
    paragraphs = soup.find("div", class_="entry-content").find_all("p")
    description = ""
    for p in paragraphs:
        if not p.find("strong"):
            description = p.get_text(strip=True)
            break
    torrents = soup.find_all("a", href=re.compile(r'magnet:\?xt=urn:btih:[^\s"]+'))
    torrent = []
    for tor in torrents:
        link = tor.get("href")
        smalls = tor.find_all("small")
        size = smalls[0].get_text(strip=True) if len(smalls) > 0 else ""
        quality = smalls[1].get_text(strip=True) if len(smalls) > 1 else ""
        torrent.append({"magnet": link, "size": size, "quality": quality})
    other_links = []
    for p in paragraphs:
        strong = p.find("strong")
        if strong and "Watch Online" in strong.get_text():
            typ = strong.get_text().split("–")[-1].strip()
            a = p.find("a")
            if a and a.get("href"):
                other_links.append({"type": typ, "url": a["href"]})

    return {
        "status": True,
        "url": url,
        "title": title,
        "description": description,
        "image": image,
        "torrent": torrent,
        "other_links": other_links
    }

@app.get("/search")
async def search(query: str):
    url = main_url+f"/search_movies?s={query}"
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

@app.get("/ss")
async def sse():
    return requests.get(main_url).content


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)

