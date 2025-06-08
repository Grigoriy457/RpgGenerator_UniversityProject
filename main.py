from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

import routes

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(routes.index.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=5000)

