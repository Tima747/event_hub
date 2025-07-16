# app/main.py
from fastapi import FastAPI
from app.api.routes import router as api_router
from app.graphql.schema import graphql_app

app = FastAPI()

app.include_router(api_router)
app.include_router(graphql_app, prefix="/graphql")  # ⬅️ ВАЖНО!

# теперь GraphQL доступен по адресу http://localhost:8000/graphql
