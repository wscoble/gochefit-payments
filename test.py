from src.handler import handle
import json


def main():
    event = dict(
        amount=0,
        dataDesc='asdfasdfasdfasdf',
        dataValue='qwerqwerqwerqwerwe'
    )

    print handle(None, event)


if __name__ == '__main__':
    main()
