from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import cloudscraper
from bs4 import BeautifulSoup

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
    try:
        req = requests.get(url).content
        soup = BeautifulSoup(req, "html.parser")
        link_elem = soup.find("a", {"class": "main-button dlbutton"})
        return link_elem['href'] if link_elem else ""
    except Exception:
        return ""

def get_page(url: str) -> list:
    try:
        req = requests.get(url).content
        soup = BeautifulSoup(req, "html.parser")
        divs = soup.find_all("div", class_="cont_display")
        data = []
        for i in range(2, len(divs)):
            title = divs[i].find("a")
            img = divs[i].find("img")
            if title and img:
                dat = {
                    "title": title.get("title") or title.get_text(strip=True),
                    "image": img.get("src", ""),
                    "link": title.get("href", "")
                }
                data.append(dat)
        return data
    except Exception as e:
        print(f"Error in get_page: {e}")
        return []

def get_movie(url: str) -> dict:
    req = requests.get(url).content
    soup = BeautifulSoup(req, "html.parser")
    
    title_elem = soup.find("h2", class_="entry-title")
    title = title_elem.get_text(strip=True).replace("Full Movie Watch Online Free", "").strip() if title_elem else "Unknown"
    
    img_elem = soup.find("img", class_="attachment-post-thumbnail")
    image = img_elem["src"] if img_elem else ""
    
    content_div = soup.find("div", class_="entry-content")
    paragraphs = content_div.find_all("p") if content_div else []
    
    description = ""
    for p in paragraphs:
        if not p.find("strong"):
            description = p.get_text(strip=True)
            break
            
    torrents = soup.find_all("a", class_="mv_button_css")
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
    url = f"{main_url}/search_movies?s={query}"
    try:
        data = get_page(url)
        total = len(data)
        main_data = {"status": True, "total_found": total, "url": url, "data": data}
    except Exception as e:
        main_data = {"status": False, "msg": "No Data Found", "error": str(e)}
    return JSONResponse(content=main_data)

@app.get("/{language}/{page}")
async def get_home(language: str, page: int = 1):
    url_map = {
        "telugu": f"{main_url}/telugu-movie/page/{page}",
        "hindi": f"{main_url}/bollywood-movie-free/page/{page}",
        "tamil": f"{main_url}/tamil-movie-free/page/{page}",
        "malayalam": f"{main_url}/malayalam-movie-online/page/{page}",
        "english": f"{main_url}/category/hollywood-movie-2023/"
    }
    url = url_map.get(language)
    if url:
        data = get_page(url)
        total = len(data)
        main_data = {"status": True, "total_found": total, "url": url, "data": data}
    else:
        main_data = {"status": False, "msg": "Invalid language category"}
    return JSONResponse(content=main_data)

@app.get("/")
async def home():
    url = f"{main_url}/"
    data = get_page(url)
    total = len(data)
    return JSONResponse(content={"status": True, "total_found": total, "url": url, "data": data})

@app.get("/fetch")
async def fetch(url: str):
    return requests.get(url).content

@app.get("/get")
async def get_s(url: str):
    try:
        data = get_movie(url)
        return JSONResponse(content=data)
    except Exception as e:
        return JSONResponse(content={"status": False, "msg": "Unable to get data", "error": str(e)})

@app.get("/ss")
async def sse():
    return requests.get(main_url).content

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
