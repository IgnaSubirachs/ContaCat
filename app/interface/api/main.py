from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
async def health_check():
    return {"status": "ok"}
