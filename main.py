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

if __name__ == '__main__':
    main()
