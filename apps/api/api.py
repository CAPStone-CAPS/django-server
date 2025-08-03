from ninja import NinjaAPI
from ninja.errors import HttpError
from django.http import JsonResponse
from .schema import ResponseSchema

from apps.group.api import group_router, group_member_router, group_vote_router
from apps.summary.api import router as summary_router
from apps.users.api import users_router
from apps.usage.api import usage_router


api = NinjaAPI()

# HttpError시 Json 형식으로 일관된 응답을 제공하는 예외 핸들러입니다.
@api.exception_handler(HttpError)
def custom_http_error_handler(request, exc: HttpError):
    return JsonResponse(
        ResponseSchema(
            message=str(exc.message),
            data=None
        ).dict(),
        status=exc.status_code
    )

api.add_router(prefix="/users", router=users_router)
api.add_router(prefix="/usage", router=usage_router)
api.add_router(prefix="/summary", router=summary_router)
api.add_router(prefix="/group", router=group_router)
api.add_router(prefix="/group", router=group_member_router)
api.add_router(prefix="/group", router=group_vote_router)

@api.get("/hello")
def hello(request):
    return {"message": "Hello, Ninja!"}
