import typing as t

from blacksheep import FromJSON, Request, json
from blacksheep.server.authorization import auth
from blacksheep.server.controllers import ApiController, delete, get, post, put

from home.schema import TaskModelIn, TaskModelOut
from home.tables import Task
from utils.cursor_pagination import CursorPagination


class Tasks(ApiController):
    # descending order
    @get()
    async def tasks(
        request: Request,
        cursor: t.Optional[str] = None,
        previous: t.Optional[str] = None,
    ) -> t.List[TaskModelOut]:
        first_row = (
            await Task.select().limit(1).order_by(Task._meta.primary_key).first().run()
        )
        last_row = (
            await Task.select()
            .order_by(Task._meta.primary_key, ascending=False)
            .limit(1)
            .first()
            .run()
        )

        previous = request.query.get("previous")
        if previous:
            paginator = CursorPagination(cursor=cursor, page_size=3, order_by="-id")
            rows_result, headers_result = await paginator.get_cursor_rows(Task, request)
            rows = await rows_result.run()
            headers = headers_result
            response = json(
                {"rows": rows[::-1]},
            )
        else:
            paginator = CursorPagination(cursor=cursor, page_size=3, order_by="-id")
            rows_result, headers_result = await paginator.get_cursor_rows(Task, request)
            rows = await rows_result.run()
            headers = headers_result
            response = json(
                {"rows": rows},
            )
        response.add_header(b"next_cursor", bytes(f"{headers['cursor']}", "utf-8"))
        response.add_header(b"last_row", bytes(f"{str(first_row['id'])}", "utf-8"))
        response.add_header(b"first_row", bytes(f"{str(last_row['id'])}", "utf-8"))
        response.add_header(b"Access-Control-Allow-Credentials", b"true")
        return response

    # ascending order
    # @get()
    # async def tasks(
    #     request: Request,
    #     cursor: t.Optional[str] = None,
    #     previous: t.Optional[str] = None,
    # ) -> t.List[TaskModelOut]:
    #     first_row = (
    #         await Task.select()
    #         .limit(1)
    #         .order_by(Task._meta.primary_key)
    #         .first()
    #         .run()
    #     )
    #     last_row = (
    #         await Task.select()
    #         .order_by(Task._meta.primary_key, ascending=False)
    #         .limit(1)
    #         .first()
    #         .run()
    #     )

    #     previous = request.query.get("previous")
    #     if previous:
    #         paginator = CursorPagination(
    #             cursor=cursor, page_size=3, order_by="id"
    #         )
    #         rows_result, headers_result = await paginator.get_cursor_rows(
    #             Task, request
    #         )
    #         rows = await rows_result.run()
    #         headers = headers_result
    #         response = json(
    #             {"rows": rows[::-1]},
    #         )
    #     else:
    #         paginator = CursorPagination(
    #             cursor=cursor, page_size=3, order_by="id"
    #         )
    #         rows_result, headers_result = await paginator.get_cursor_rows(
    #             Task, request
    #         )
    #         rows = await rows_result.run()
    #         headers = headers_result
    #         response = json(
    #             {"rows": rows},
    #         )
    #     response.add_header(
    #         b"next_cursor", bytes(f"{headers['cursor']}", "utf-8")
    #     )
    #     response.add_header(
    #         b"first_row", bytes(f"{str(first_row['id'])}", "utf-8")
    #     )
    #     response.add_header(
    #         b"last_row", bytes(f"{str(last_row['id'])}", "utf-8")
    #     )
    #     return response

    @auth("authenticated")
    @post()
    async def create_task(task_model: FromJSON[TaskModelIn]) -> TaskModelOut:
        task = Task(**task_model.value.dict())
        await task.save()
        return TaskModelOut(**task.to_dict())

    @auth("authenticated")
    @put("{task_id}")
    async def put_task(task_id: int, task_model: FromJSON[TaskModelIn]) -> TaskModelOut:
        task = await Task.objects().get(Task.id == task_id)
        if not task:
            return json({}, status=404)

        for key, value in task_model.value.dict().items():
            setattr(task, key, value)

        await task.save()

        return TaskModelOut(**task.to_dict())

    @auth("authenticated")
    @delete("{task_id}")
    async def delete_task(task_id: int):
        task = await Task.objects().get(Task.id == task_id)
        if not task:
            return json({}, status=404)

        await task.remove()
