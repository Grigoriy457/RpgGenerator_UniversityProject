from fastapi import APIRouter, Request, Form, status, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from itsdangerous import URLSafeSerializer
from email_validator import validate_email, EmailNotValidError

import config
import database


router = APIRouter()

templates = Jinja2Templates(directory="templates")
serializer = URLSafeSerializer(config.CSRF_SECRET)


def flash(request: Request, message: str):
    request.session["_flash"] = message

def get_flash(request: Request):
    msg = request.session.pop("_flash", None)
    return msg


@router.get("/register")
async def index_handler(request: Request):
    if request.session.get("user") is not None:
        return RedirectResponse("/", status_code=303)

    token = serializer.dumps("register")
    form_data = request.session.get("form_data", {})
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "csrf_token": token,
            "flash_message": get_flash(request),
            "username": form_data.get("username", ""),
            "email": form_data.get("email", ""),
            "password": form_data.get("password", ""),
        }
    )


@router.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    csrf_token: str = Form(...)
):
    request.session["form_data"] = {"username": username, "email": email, "password": password}
    if serializer.loads(csrf_token) != "register":
        flash(request, "Неверный CSRF токен!")
        return RedirectResponse("/register", status_code=303)

    if password != confirm_password:
        flash(request, "Пароли не совпадают!")
        return RedirectResponse("/register", status_code=303)

    try:
        email_info = validate_email(email, check_deliverability=False)
        email = email_info.normalized
    except EmailNotValidError as e:
        flash(request, f"Неверный email: {str(e)}")
        return RedirectResponse("/register", status_code=303)

    async with database.Database() as db:
        async with db.session() as db_session:
            db_user = await db_session.scalar(
                database.select(database.models.auth.User)
                .where(database.models.auth.User.email == email)
            )
            if db_user is not None:
                flash(request, "Этот email уже привязан к другой учётной записи!")
                return RedirectResponse("/register", status_code=303)

            db_user = await db_session.merge(database.models.auth.User(
                username=username,
                email=email,
                password=password
            ))
            await db_session.commit()
            await db_session.refresh(db_user)

    request.session["user"] = {"id": db_user.id, "username": db_user.username}
    request.session.pop("form_data", None)
    return RedirectResponse("/", status_code=303)


@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    if request.session.get("user") is not None:
        return RedirectResponse("/", status_code=303)

    token = serializer.dumps("login")
    return templates.TemplateResponse(
        "login.html", {"request": request, "csrf_token": token, "flash_message": get_flash(request)}
    )

@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...)
):
    if serializer.loads(csrf_token) != "login":
        flash(request, "Неверный CSRF токен!")
        return RedirectResponse("/login", status_code=303)

    async with database.Database().session() as db_session:
        db_user = await db_session.scalar(
            database.select(database.models.auth.User)
            .where(database.models.auth.User.email == email)
        )

        if db_user is None:
            flash(request, "Пользователь с таким email не найден!")
            return RedirectResponse("/login", status_code=303)

        if db_user.password != password:
            flash(request, "Неверный пароль!")
            return RedirectResponse("/login", status_code=303)

    request.session["user"] = {"id": db_user.id, "username": db_user.username}
    return RedirectResponse("/", status_code=303)


@router.get("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse("/", status_code=303)
