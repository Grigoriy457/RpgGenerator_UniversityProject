from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

import database


router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/profile/")
async def index_handler(request: Request):
    if request.session.get("user") is None:
        return RedirectResponse("/login", status_code=303)

    async with database.Database().session() as db_session:
        db_user = await db_session.scalar(
            database.select(database.models.auth.User)
            .where(database.models.auth.User.id == int(request.session["user"]["id"]))
        )
        my_games = (await db_session.scalars(
            database.select(database.models.game.Game)
            .where(database.models.game.Game.owner_id == db_user.id)
            .order_by(database.models.game.Game.created_at.desc())
        )).all()
    return templates.TemplateResponse(
        "profile.html", {
            "request": request,
            "user": db_user,
            "my_games": my_games
        }
    )
