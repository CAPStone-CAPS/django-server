from ninja import NinjaAPI
from apps.group.api import group_router, group_member_router

api = NinjaAPI()

api.add_router(prefix="/group", router=group_router)
api.add_router(prefix="/group", router=group_member_router)

@api.get("/hello")
def hello(request):
    return {"message": "Hello, Ninja!"}
