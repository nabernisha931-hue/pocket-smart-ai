from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(
    directory="app/templates"
)


router = APIRouter(
    tags=["pages"]
)


@router.get(
    "/",
    response_class=HTMLResponse
)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request
        }
    )


@router.get(
    "/login",
    response_class=HTMLResponse
)
def login(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "request": request
        }
    )


@router.get(
    "/register",
    response_class=HTMLResponse
)
def register(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={
            "request": request
        }
    )


@router.get(
    "/dashboard",
    response_class=HTMLResponse
)
def dashboard(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "request": request
        }
    )


@router.get(
    "/history",
    response_class=HTMLResponse
)
def history(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={
            "request": request
        }
    )


@router.get(
    "/planner/{planner}",
    response_class=HTMLResponse
)
def planner(
    request: Request,
    planner: str
):

    if planner not in {
        "home",
        "party",
        "jewelry"
    }:
        planner = "home"

    return templates.TemplateResponse(
        request=request,
        name="planner.html",
        context={
            "request": request,
            "planner": planner,
        }
    )