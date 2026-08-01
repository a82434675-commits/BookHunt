from fastapi import APIRouter, Form, Request, HTTPException
from fastapi.responses import RedirectResponse
from src.auth import (
    is_valid_username,
    is_valid_gmail,
    is_strong_password,
    username_exists,
    email_exists,
    create_pending_signup,
    verify_pending_code,
    finalize_signup,
    verify_user,
    create_session,
    delete_session,
    get_username_from_token,
    delete_user,
    delete_all_sessions_for_user
)
from src.email_utils import send_verification_email

router = APIRouter(tags=["Auth"])

COOKIE_MAX_AGE = 60 * 60 * 24 * 365 * 10


@router.post("/auth/signup")
async def signup(username: str = Form(...), email: str = Form(...), password: str = Form(...)):

    if not is_valid_username(username):
        return RedirectResponse(url="/login?error=Username must contain letters only (no numbers or symbols)", status_code=303)

    if username_exists(username):
        return RedirectResponse(url="/login?error=Username already exists", status_code=303)

    if not is_valid_gmail(email):
        return RedirectResponse(url="/login?error=Please enter a valid Gmail address", status_code=303)

    if email_exists(email):
        return RedirectResponse(url="/login?error=This Gmail is already registered", status_code=303)

    if not is_strong_password(password):
        return RedirectResponse(
            url="/login?error=Password must be 8+ characters with uppercase, lowercase, a number, and a special character",
            status_code=303
        )

    code = create_pending_signup(username, email, password)

    try:
        send_verification_email(email, code)
    except Exception:
        return RedirectResponse(url="/login?error=Could not send verification email. Check SMTP settings.", status_code=303)

    return RedirectResponse(url=f"/verify?email={email}", status_code=303)


@router.post("/auth/verify")
async def verify(email: str = Form(...), code: str = Form(...)):
    entry, error = verify_pending_code(email, code)

    if error:
        return RedirectResponse(url=f"/verify?email={email}&error={error}", status_code=303)

    finalize_signup(email)
    token = create_session(entry["username"])

    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="session_token", value=token, httponly=True, max_age=COOKIE_MAX_AGE)
    return response


@router.post("/auth/login")
async def login(username: str = Form(...), password: str = Form(...)):
    if not verify_user(username, password):
        return RedirectResponse(url="/login?error=Invalid username or password", status_code=303)

    token = create_session(username)
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="session_token", value=token, httponly=True, max_age=COOKIE_MAX_AGE)
    return response


@router.get("/auth/logout")
async def logout(request: Request):
    token = request.cookies.get("session_token")
    if token:
        delete_session(token)

    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("session_token")
    return response


@router.get("/auth/me")
async def me(request: Request):
    token = request.cookies.get("session_token")
    username = get_username_from_token(token)

    if not username:
        raise HTTPException(status_code=401, detail="Not logged in")

    return {"username": username}


@router.post("/auth/delete-account")
async def delete_account(request: Request):
    token = request.cookies.get("session_token")
    username = get_username_from_token(token)

    if not username:
        raise HTTPException(status_code=401, detail="Not logged in")

    delete_all_sessions_for_user(username)
    delete_user(username)

    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("session_token")
    return response
