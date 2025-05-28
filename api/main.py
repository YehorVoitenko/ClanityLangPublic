from fastapi import FastAPI

from .routers.promocodes.router import promocodes_router
from .routers.subscriptions.router import subscription_router
from .routers.user.router import user_router

app = FastAPI()
app.include_router(user_router)
app.include_router(subscription_router)
app.include_router(promocodes_router)
