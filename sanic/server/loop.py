"""Event loop setup."""
import asyncio


def try_use_uvloop():
    """Try to use uvloop."""
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        return True
    except ImportError:
        return False
