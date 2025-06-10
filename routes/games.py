from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import sqlalchemy
import base64

import database


router = APIRouter(prefix="/games")

templates = Jinja2Templates(directory="templates")


@router.get("/")
async def index_handler(request: Request):
    async with database.Database().session() as db_session:
        last_added_games = await db_session.scalars(
            database.select(database.models.game.Game)
            .order_by(database.models.game.Game.created_at.desc())
            .limit(5)
        )
        popular_games = await db_session.scalars(
            database.select(database.models.game.Game)
            .order_by(database.models.game.Game.views.desc())
            .limit(5)
        )

    return templates.TemplateResponse(
        "games/index.html",
        {
            "request": request,
            "last_added_games": last_added_games,
            "popular_games": popular_games
        }
    )


@router.get("/all/")
async def all_handler(request: Request):
    async with database.Database().session() as db_session:
        all_games = await db_session.scalars(
            database.select(database.models.game.Game)
            .order_by(database.models.game.Game.views.desc())
        )

    return templates.TemplateResponse(
        "games/all.html",
        {
            "request": request,
            "all_games": all_games
        }
    )


@router.get("/{game_id}/")
async def game_handler(game_id: int, request: Request):
    async with database.Database().session() as db_session:
        game = await db_session.scalar(
            database.select(database.models.game.Game)
            .where(database.models.game.Game.id == game_id)
        )
        if game is None:
            raise HTTPException(status_code=404, detail="Game not found")

        return templates.TemplateResponse(
            "games/game.html",
            {
                "request": request,
                "game": game,
                "owner": await game.awaitable_attrs.owner,
                "characters": await game.awaitable_attrs.characters,
                "rules": await game.awaitable_attrs.rules
            }
        )


@router.get("/{game_id}/edit/")
async def edit_game(game_id: int, request: Request):
    async with database.Database().session() as db_session:
        game = await db_session.scalar(
            database.select(database.models.game.Game)
            .where(database.models.game.Game.id == game_id)
        )
        if game is None:
            raise HTTPException(status_code=404, detail="Game not found")
        if game.owner_id != request.session.get("user", {"id": None})["id"]:
            raise HTTPException(status_code=403, detail="You do not have permission to edit this game")

        return templates.TemplateResponse(
            "games/edit.html",
            {
                "request": request,
                "game": game,
                "owner": await game.awaitable_attrs.owner,
                "characters": await game.awaitable_attrs.characters,
                "rules": await game.awaitable_attrs.rules,
                "genres": database.models.game.GameGenre
            }
        )


@router.post("/{game_id}/edit/")
async def update_game(game_id: int, request: Request):
    form_data = await request.form()
    async with database.Database().session() as db_session:
        game = await db_session.scalar(
            database.select(database.models.game.Game)
            .where(database.models.game.Game.id == game_id)
        )
        if game is None:
            raise HTTPException(status_code=404, detail="Game not found")
        if game.owner_id != request.session.get("user", {"id": None})["id"]:
            raise HTTPException(status_code=403, detail="You do not have permission to edit this game")

        # Обновление основных данных игры
        game.title = form_data.get("title")
        game.description = form_data.get("description")
        game.genre = form_data.get("genre")
        game.is_public = form_data.get("is_public") == "on"

        # Удаление старых персонажей и правил
        await db_session.execute(
            sqlalchemy.delete(database.models.game.Character)
            .where(database.models.game.Character.game_id == game_id)
        )
        await db_session.execute(
            sqlalchemy.delete(database.models.game.Rule)
            .where(database.models.game.Rule.game_id == game_id)
        )

        # Добавление новых персонажей
        new_characters = []
        for character_id, character_avatar_base64, name, description, avatar in zip(
            form_data.getlist("character_id[]"),
            form_data.getlist("character_avatar_base64[]"),
            form_data.getlist("character_name[]"),
            form_data.getlist("character_description[]"),
            form_data.getlist("character_avatar[]"),
        ):
            new_characters.append(
                database.models.game.Character(
                    id=int(character_id) if character_id != "" else None,
                    name=name,
                    description=description,
                    avatar=avatar.file.read() if avatar.size > 0 else
                        (base64.b64decode(character_avatar_base64) if character_avatar_base64 else None),
                    game_id=game_id,
                )
            )
        db_session.add_all(new_characters)

        # Добавление новых правил
        new_rules = []
        for rule_id, name, description in zip(
            form_data.getlist("rule_id[]"),
            form_data.getlist("rule_name[]"),
            form_data.getlist("rule_description[]"),
        ):
            new_rules.append(
                database.models.game.Rule(
                    id=int(rule_id) if rule_id != "" else None,
                    name=name,
                    description=description,
                    game_id=game_id,
                )
            )
        db_session.add_all(new_rules)
        await db_session.commit()

    return RedirectResponse(f"/games/{game_id}/", status_code=303)
