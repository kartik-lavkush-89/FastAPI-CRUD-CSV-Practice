from fastapi import FastAPI
from src.routes.views import app1


'''MAIN APP FILE'''


app = FastAPI()
app.include_router(app1)

