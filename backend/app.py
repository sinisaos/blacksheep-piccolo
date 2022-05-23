from blacksheep import Application, json
from blacksheep.server.openapi.v3 import OpenAPIHandler
from openapidocs.v3 import Info
from piccolo.apps.user.tables import BaseUser
from piccolo.engine import engine_finder
from piccolo_admin.endpoints import create_admin
from piccolo_api.session_auth.tables import SessionsBase

from accounts.endpoints import AuthController
from home.endpoints import Tasks
from home.tables import Task

app = Application(show_error_details=True)


app.use_cors(
    allow_origins="http://localhost:8080",
    allow_methods="*",
    allow_headers="*",
    allow_credentials=True,
    expose_headers="next_cursor,first_row,last_row",
)

# mount Piccolo ASGI apps
app.mount(
    "/admin/",
    create_admin(
        tables=[Task, BaseUser, SessionsBase],
        # Required when running under HTTPS:
        # allowed_hosts=['my_site.com']
    ),
)

# Openpi docs
docs = OpenAPIHandler(info=Info(title="BlackSheep API", version="0.0.1"))
docs.bind_app(app)


@docs.ignore()
async def home(request) -> json:
    try:
        data = (
            await SessionsBase.select(SessionsBase.user_id)
            .where(SessionsBase.token == request.cookies.get("id"))
            .first()
            .run()
        )
        if data:
            session_user = (
                await BaseUser.select(BaseUser.username)
                .where(BaseUser._meta.primary_key == data["user_id"])
                .first()
                .run()
            )
        auth_user = session_user["username"]
    except UnboundLocalError:
        auth_user = ""
    response = json(
        {
            "message": "BlackSheep Piccolo ORM api",
            "auth_user": auth_user,
        }
    )
    response.add_header(b"Access-Control-Allow-Credentials", b"true")
    return response


app.router.add_get("/", home)


async def open_database_connection_pool(application):
    try:
        engine = engine_finder()
        await engine.start_connection_pool()
    except Exception:
        print("Unable to connect to the database")


async def close_database_connection_pool(application):
    try:
        engine = engine_finder()
        await engine.close_connection_pool()
    except Exception:
        print("Unable to connect to the database")


app.on_start += open_database_connection_pool
app.on_stop += close_database_connection_pool
