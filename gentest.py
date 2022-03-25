import json

from fastapi import Response

from namegen.server import app


class PrettyResponse(Response):
    media_type = "application/json"

    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            indent=4
        ).encode("utf-8")


@app.get('/test', response_class=PrettyResponse)
async def generate_all_drivers(n: int = 100_000):
    import time, os, gc
    import psutil
    from namegen import driver_memory, driver_sqlite, driver_hybrid
    labels = ['sqlite', 'memory', 'hybrid', ]
    data = list()
    for d in [
        driver_sqlite.SQLiteDriver(),
        driver_memory.MemoryDriver(),
        driver_hybrid.HybridDriver(),
    ]:
        d.start()
        try:
            p = psutil.Process(os.getpid())
            gc.disable()
            gc.collect()
            memory_start = p.memory_info()[0]
            start_time = time.time()
            for _ in range(0, n):
                d.generate()
            end_time = time.time()
            memory_end = p.memory_info()[0]
            gc.enable()
            data.append(
                dict(
                    time=f'{(end_time - start_time) * 1000:.2f} ms',
                    memory_increase=f'{(memory_end / memory_start * 100) - 100:.2f}%',
                    memory_maximum=f'{memory_end * 1E-6:.2f} mb',
                    memory_minimum=f'{memory_start * 1E-6:.2f} mb'
                )
            )
        finally:
            d.stop()
    out = dict(zip(labels, data))
    out['count'] = n
    return out


app = app
