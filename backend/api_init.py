from fastapi import FastAPI
from routers import example

app = FastAPI()

app.include_router(example.router)

'''
Check if the backend opened successfully
'''
@app.get('/')
def root():
    return {'backend status': 'open'}