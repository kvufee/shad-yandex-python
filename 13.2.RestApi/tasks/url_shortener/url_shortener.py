import uuid
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel


app = FastAPI()
url_mapping: dict[str, str] = {}
key_mapping: dict[str, str] = {}


class ToShort(BaseModel):
    url: str


class Shorted(BaseModel):
    url: str
    key: str


@app.post("/shorten", response_model=Shorted, status_code=201, summary="Short Url", operation_id="short_url_shorten_post")
def shorten_url(to_short: ToShort):
    url = to_short.url
    if url in key_mapping:
        key = key_mapping[url]
    else:
        key = str(uuid.uuid4())[:6]
        key_mapping[url] = key
        url_mapping[key] = url
    return Shorted(url=url, key=key)


@app.get("/go/{key}", status_code=307, summary="Redirect To Url", operation_id="redirect_to_url_go__key__get",
         responses={
             307: {"description": "Successful Response"},
             404: {"description": "Key not found"}
         })
def redirect_to_url(key: str):
    if key in url_mapping:
        url = url_mapping[key]
        return RedirectResponse(url)
    else:
        raise HTTPException(status_code=404, detail="Key not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)