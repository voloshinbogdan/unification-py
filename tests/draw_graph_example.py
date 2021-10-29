from inheritance_parser import *


def main():
    p = parse_file('example8.txt')
    inheritance = build_graph('example8', p['parents'])

    inheritance.format = 'png'
    inheritance.view(cleanup=True)


if __name__ == '__main__':
    main()