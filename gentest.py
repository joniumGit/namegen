from namegen.server import app


@app.get('/test')
async def generate_all_drivers():
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
            for _ in range(0, 100_000):
                d.generate()
            end_time = time.time()
            memory_end = p.memory_info()[0]
            gc.enable()
            data.append(f'time: {(end_time - start_time) * 1000:.4f} ms memory delta: {memory_end - memory_start}')
        finally:
            d.stop()
    return dict(zip(labels, data))


app = app
