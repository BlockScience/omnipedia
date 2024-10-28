from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager

from auth.jwt_bearer import JWTBearer
from config.config import initiate_database
from routes.admin import router as AdminRouter
from routes.student import router as StudentRouter
from routes.styleguide import router as StyleGuideRouter

app = FastAPI()

token_listener = JWTBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await initiate_database()
    yield


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to this fantastic app."}


app.include_router(AdminRouter, tags=["Administrator"], prefix="/admin")
app.include_router(
    StudentRouter,
    tags=["Students"],
    prefix="/student",
    dependencies=[Depends(token_listener)],
)
app.include_router(StyleGuideRouter)
