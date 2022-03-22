import os

from fastapi import FastAPI
from pydantic import BaseModel

if os.getenv('NAMEGEN_USE_SQLITE', 'false').lower() == 'true':  # pragma nocover
    from .driver_sqlite import generate, start, stop
else:
    from .driver_memory import generate, start, stop

app = FastAPI()


class Name(BaseModel):
    value: str


@app.get(
    '/',
    name='name',
    response_model=Name,
    responses={
        200: {
            'description': 'Success',
            'value': {
                'example': {
                    'application/json': {
                        'value': 'CoolSquirrel#3713'
                    }
                }
            }
        }
    }
)
def get_name():
    return Name.construct(value=generate())


@app.get('/test')
def test_gen():  # pragma nocover
    from . import driver_memory as mem, driver_sqlite as db
    db.start()
    mem.start()
    try:
        import time

        start_time = time.time()
        data = list()
        for _ in range(0, 1000):
            data.append(db.generate())
        end_time = time.time()
        db_time = end_time - start_time

        start_time = time.time()
        data = list()
        for _ in range(0, 1000):
            data.append(mem.generate())
        end_time = time.time()
        mem_time = end_time - start_time

        return {'mem': mem_time, 'db': db_time}
    finally:
        mem.stop()
        db.stop()


@app.on_event('startup')
def startup():
    start()


@app.on_event('shutdown')
def shutdown():
    stop()
