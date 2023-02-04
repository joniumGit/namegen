import os
import textwrap
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel, constr

from ..driver import Driver


def _import_driver(choice: Optional[str]) -> Driver:
    choice = choice.lower() if choice is not None else ''
    if choice == 'sqlite':
        from ..driver_sqlite import SQLiteDriver as Generator
    elif choice == 'memory':
        from ..driver_memory import MemoryDriver as Generator
    else:
        from ..driver_hybrid import HybridDriver as Generator
    return Generator()


app = FastAPI(
    title="Namegen",
    version="2.1.0",
    openapi_tags=[
        {
            'name': 'Namegen',
            'description': 'Default Operations'
        }
    ],
    description=textwrap.dedent(
        """
        ## Namegen
        
        Generates names of the format AaaaBbbb#1234
        """
    ),
)
driver: Driver


class Name(BaseModel):
    value: constr(strip_whitespace=True, regex=r'\w+#\d{4}')


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
    },
    tags=["Namegen"],
)
async def get_name():
    return Name.construct(value=driver.generate())


@app.on_event('startup')
async def startup():
    global driver
    driver = _import_driver(os.getenv('NAMEGEN_DRIVER'))
    driver.start()


@app.on_event('shutdown')
async def shutdown():
    global driver
    driver.stop()
