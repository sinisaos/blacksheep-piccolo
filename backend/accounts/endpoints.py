from blacksheep import FromJSON, Response, json
from blacksheep.cookies import Cookie
from blacksheep.server.controllers import Controller, get, post, delete
from blacksheep.server.responses import redirect
from piccolo.apps.user.tables import BaseUser
from piccolo_api.session_auth.tables import SessionsBase

from accounts.schema import UserModelLogin, UserModelRegister
from home.tables import Task


class AuthController(Controller):
    @post("/register")
    async def register(request, data: FromJSON[UserModelRegister]):
        """
        Register and authenticate user
        """
        data = data.__dict__
        payload = data["_value"].dict()
        if (
            await BaseUser.exists()
            .where(BaseUser.email == payload["email"])
            .run()
            or await BaseUser.exists()
            .where(BaseUser.username == payload["username"])
            .run()
        ):
            user_error = "User with that email or username already exists."
            return json({"error": user_error})
        # save user
        query = BaseUser(**payload)
        await query.save().run()
        # login user in
        valid_user = await BaseUser.login(
            username=payload["username"], password=payload["password"]
        )
        if not valid_user:
            user_error = "Invalid username or password"
            return json({"error": user_error})
        # create session
        session = await SessionsBase.create_session(user_id=valid_user)
        response = redirect("/")
        response.set_cookie(
            Cookie(
                "id",
                f"{session['token']}",
            )
        )
        response.add_header(b"Access-Control-Allow-Credentials", b"true")
        return response

    @post("/login")
    async def login(request, data: FromJSON[UserModelLogin]):
        """
        Login and authenticate user
        """
        data = data.__dict__
        payload = data["_value"].dict()
        # login user in
        valid_user = await BaseUser.login(
            username=payload["username"], password=payload["password"]
        )
        if not valid_user:
            user_error = "Invalid username or password"
            return json({"error": user_error})
        # create session
        session = await SessionsBase.create_session(user_id=valid_user)
        response = redirect("/profile")
        response.set_cookie(
            Cookie(
                "id",
                f"{session['token']}",
                http_only=True,
            )
        )
        response.add_header(b"Access-Control-Allow-Credentials", b"true")
        return response

    @get("/profile")
    async def profile(request):
        """
        User profile
        """
        data = (
            await SessionsBase.select(SessionsBase.user_id)
            .where(SessionsBase.token == request.cookies.get("id"))
            .first()
            .run()
        )
        if data:
            session_user = (
                await BaseUser.select(
                    BaseUser.id,
                    BaseUser.username,
                    BaseUser.email,
                    BaseUser.last_login,
                )
                .where(BaseUser._meta.primary_key == data["user_id"])
                .first()
                .run()
            )
        user = session_user
        response = json(
            {
                "user": user,
            }
        )
        response.add_header(b"Access-Control-Allow-Credentials", b"true")
        return response

    @get("/profile/tasks")
    async def profile_tasks(request):
        """
        Profile tasks
        """
        data = (
            await SessionsBase.select(SessionsBase.user_id)
            .where(SessionsBase.token == request.cookies.get("id"))
            .first()
            .run()
        )
        if data:
            session_user = (
                await BaseUser.select(
                    BaseUser.id,
                    BaseUser.username,
                    BaseUser.email,
                    BaseUser.last_login,
                )
                .where(BaseUser._meta.primary_key == data["user_id"])
                .first()
                .run()
            )
        user = session_user
        tasks = (
            await Task.select()
            .where(Task.task_user == session_user["id"])
            .order_by(Task.id, ascending=False)
            .run()
        )
        response = json(tasks)
        response.add_header(b"Access-Control-Allow-Credentials", b"true")
        return response

    @post("/logout")
    async def logout(request):
        """
        Logout user
        """
        response = redirect("/")
        response.unset_cookie("id")
        response.add_header(b"Access-Control-Allow-Credentials", b"true")
        return response

    @delete("/delete")
    async def delete_user(request):
        data = (
            await SessionsBase.select(SessionsBase.user_id)
            .where(SessionsBase.token == request.cookies.get("id"))
            .first()
            .run()
        )
        if data:
            session_user = (
                await BaseUser.select(
                    BaseUser.id,
                    BaseUser.username,
                    BaseUser.email,
                    BaseUser.last_login,
                )
                .where(BaseUser._meta.primary_key == data["user_id"])
                .first()
                .run()
            )
        user = session_user
        await BaseUser.delete().where(BaseUser.id == session_user["id"]).run()

        response = Response(204)
        response.unset_cookie("id")
        response.add_header(b"Access-Control-Allow-Credentials", b"true")
        return response
