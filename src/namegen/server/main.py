import os

from fastapi import FastAPI
from pydantic import BaseModel

if os.getenv('NAMEGEN_USE_SQLITE', 'false').lower() == 'true':  # pragma nocover
    from ..driver_sqlite import SQLiteDriver as Driver
else:
    from ..driver_memory import MemoryDriver as Driver

app = FastAPI()
driver = Driver()


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
async def get_name():
    return Name.construct(value=driver.generate())


@app.get('/test')
async def test_gen():  # pragma nocover
    from .. import driver_memory, driver_sqlite
    db = driver_sqlite.SQLiteDriver()
    mem = driver_memory.MemoryDriver()
    mem.start()
    db.start()
    try:
        import time

        start_time = time.time()
        data = list()
        for _ in range(0, 1000):
            data.append(db.generate())
        end_time = time.time()
        db_time = (end_time - start_time) * 1000

        start_time = time.time()
        data = list()
        for _ in range(0, 1000):
            data.append(mem.generate())
        end_time = time.time()
        mem_time = (end_time - start_time) * 1000

        return {'memory': mem_time, 'sqlite': db_time}
    finally:
        mem.stop()
        db.stop()


@app.on_event('startup')
async def startup():
    driver.start()


@app.on_event('shutdown')
async def shutdown():
    driver.start()
