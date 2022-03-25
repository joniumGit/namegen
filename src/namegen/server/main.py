import os

from fastapi import FastAPI
from pydantic import BaseModel

__driver_choice = os.getenv('NAMEGEN_DRIVER', 'memory').lower()
if __driver_choice == 'sqlite':  # pragma nocover
    from ..driver_sqlite import SQLiteDriver as Driver
elif __driver_choice == 'hybrid':
    from ..driver_hybrid import HybridDriver as Driver
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


@app.on_event('startup')
async def startup():
    driver.start()


@app.on_event('shutdown')
async def shutdown():
    driver.start()
