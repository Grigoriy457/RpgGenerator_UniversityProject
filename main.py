from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

import routes
import config

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=config.SECRET_KEY)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(routes.index.router)
app.include_router(routes.auth.router)
app.include_router(routes.games.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)

