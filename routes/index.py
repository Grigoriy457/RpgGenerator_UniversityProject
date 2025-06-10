from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

import database


router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/")
async def index_handler(request: Request):
    async with database.Database().session() as db_session:
        popular_games = await db_session.scalars(
            database.select(database.models.game.Game)
            .where(database.models.game.Game.is_public.is_(True))
            .order_by(database.models.game.Game.views.desc())
            .limit(5)
        )
    return templates.TemplateResponse(
        "index.html", {
            "request": request,
            "popular_games": popular_games
        }
    )
