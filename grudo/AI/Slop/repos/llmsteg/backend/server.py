from fastapi import FastAPI, Request

from stegano import encode_message, decode_message
import logging

app = FastAPI()

# Setting up basic logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/")
async def read_root():
    logger.info("GET / - Hello World requested")
    return {"message": "Hello World"}


@app.post("/encode")
async def encode(request: Request):
    data = await request.json()
    message = data.get("message")
    prompt = data.get("prompt")
    logger.info(f"POST /encode - message: {message}, prompt: {prompt}")
    encoded = encode_message(message, prompt=prompt)
    return {"encoded_message": encoded}


@app.post("/decode")
async def decode(request: Request):
    data = await request.json()
    cover_text = data.get("cover_text")
    prompt = data.get("prompt")
    logger.info(f"POST /decode - cover_text: {cover_text}, prompt: {prompt}")
    decoded = decode_message(cover_text, prompt=prompt)
    return {"decoded_message": decoded}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
