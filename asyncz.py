import asyncio
import inspect
import functools
from typing import AsyncGenerator, Callable

__alist = []
asleep = asyncio.sleep


def _registerFuture(fut):
    __alist.append(fut)


def az(func):

    @functools.wraps(func)
    def wrapper(*args, **kwarg):
        fut = asyncio.ensure_future(func(*args, **kwarg))
        _registerFuture(fut)
        return fut
    return wrapper


def waitAll():
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(__alist))
    except ValueError:
        pass


def mainz(func):
    @functools.wraps(func)
    def wrapper(*args, **kwarg):

        frame = inspect.stack()[-1][0]
        for key, val in frame.f_locals.items():
            if inspect.iscoroutinefunction(val):
                frame.f_locals[key] = az(val)
        # ----------------------------------------
        if inspect.iscoroutinefunction(func):
            loop = asyncio.get_event_loop()
            res = loop.run_until_complete(func(*args, **kwarg))
        else:
            res = func(*args, **kwarg)
        waitAll()
        return res
    return wrapper


#---------------------Stream's Section

class StreamListenException(Exception):
    def __init__(self, *args, **kwarg):
        super().__init__("The stream should be listend only once.", *args, **kwarg)
        # pass


class Stream:

    def __init__(self, agen: AsyncGenerator) -> None:
        self.agen = agen
        self._started = False
        self._future: list = []
        self._where_condition: Callable
        _registerFuture(self)

    def __aiter__(self):
        if self._started:
            raise StreamListenException
        self._started = True
        return self

    async def __anext__(self):
        if self._where_condition:
            while True:
                res = await self.agen.asend(None)
                if self._where_condition(res):
                    return res
                else:
                    continue
        else:
            return await self.agen.asend(None)

    def where(self, func: Callable):
        # new_stream: Stream = Stream(self.agen)
        self._where_condition = func
        return self

    def listen(self, func: Callable) -> None:
        if self._started:
            raise StreamListenException
        f = asyncio.ensure_future(self._start_listen(func))
        self._future.append(f)
        self._started = True

    async def _start_listen(self, func: Callable) -> None:
        if self._where_condition:
            async for i in self.agen:
                if self._where_condition(i):
                    func(i)
        else:
            async for i in self.agen:
                func(i)

    async def join(self):
        try:
            await asyncio.wait(self._future)
        except ValueError:
            pass

    def asBroadcast(self):
        if isinstance(self, BroadcastStream):
            raise AttributeError('BroadcastStream does\'s have asBroadcast or at lease it\'s disable.')
        else:
            return BroadcastStream(self.agen)

    def __await__(self):
        if self._future:
            return asyncio.wait(self._future).__await__()
        else:
            async def _temp():
                pass
            return _temp().__await__()


class BroadcastStream(Stream):

    def __init__(self, agen: AsyncGenerator) -> None:
        super().__init__(agen)
        self._callbacks: list = []

    def listen(self, func: Callable) -> None:
        self._callbacks.append(func)
        if not self._started:
            self._started = True
            runner = asyncio.ensure_future(self._start_listen())
            self._future.append(runner)

    async def _start_listen(self):
        async for i in self.agen:
            for func in self._callbacks:
                func(i)


def streamize(func):
    @functools.wraps(func)
    def inner(*args, **kwarg):
        return Stream(func(*args, **kwarg))
    return inner
