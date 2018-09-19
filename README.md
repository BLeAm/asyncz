# asyncz
Utility wrapper that makes asynchronous in Python more simple.

```python
from asyncio import sleep
from asyncz import mainz


async def timer(sec: int) -> int:
    await sleep(sec)
    return sec


async def printAfter(sec: int, text: str) -> None:
    await sleep(sec)
    print(text)


@mainz
async def main() -> None:
    printAfter(1, 'first try.')
    print('something')
    printAfter(3, 'second try.')
    print('value from await timer:', await timer(1))
    print(f'print after "{await timer(3)}" secs')
    print(f'print after "{await timer(2)}" secs')

if __name__ == '__main__':
    main()

```

result:

```
something
first try.
value from await timer: 1
second try.
print after "3" secs
print after "2" secs
```