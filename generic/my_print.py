from time import localtime, ticks_ms

def timestamp():
    t = localtime()
    ms = ticks_ms() % 1000
    return "{:02d}:{:02d}:{:02d}.{:03d}".format(
        t[3], t[4], t[5], ms
    )

def my_print(*args):
    print(f"{timestamp()}:", *args)