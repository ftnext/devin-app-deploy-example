# /// script
# dependencies = ["fastapi>=0.138.0", "uvicorn"]
# ///

import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI

app = FastAPI()
app.frontend("/", directory=Path(__file__).resolve().parent / "slides")

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", "8000")),
    )
