import os
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel


def _import_driver(choice: Optional[str]):
    choice = choice.lower() if choice is not None else ''
    if choice == 'sqlite':
        from ..driver_sqlite import SQLiteDriver as Driver
    elif choice == 'memory':
        from ..driver_memory import MemoryDriver as Driver
    else:
        from ..driver_hybrid import HybridDriver as Driver
    return Driver()


app = FastAPI()
driver = _import_driver(os.getenv('NAMEGEN_DRIVER'))


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
