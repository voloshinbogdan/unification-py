from inheritance_parser import *

inheritance = None


def main():
    global inheritance
    p = parse_file('example8.txt')
    inheritance = build_graph('example8', p['parents'])

    inheritance.format = 'png'


if __name__ == '__main__':
    main()
    inheritance.view(cleanup=True)
