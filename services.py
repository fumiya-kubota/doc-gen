import click


@click.group()
def cmd():
    pass


@cmd.command()
def generate():
    pass


@cmd.command()
def image():
    from lib.fetch_resources import fetch_image
    for resource in fetch_image(5):
        print(resource)


@cmd.command()
def hand():
    from lib.fetch_resources import fetch_handwriting
    for resource in fetch_handwriting(5):
        print(resource)


@cmd.command()
def graph():
    from lib.fetch_resources import fetch_graph
    for resource in fetch_graph(5):
        print(resource)


if __name__ == '__main__':
    cmd()
