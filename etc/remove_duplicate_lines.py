import fileinput
import argparse


def printer(line, strip):
    if strip:
        print(line)
    else:
        print(line,end="")

if __name__ == "__main__" :

    parser=argparse.ArgumentParser()
    parser.add_argument("--strip", default="False", action="store_true", help="Strip whitespace on input")
    parser.add_argument('files', metavar='FILE', nargs='*', help='files to read, if empty, stdin is used')
    args=parser.parse_args()

    line_stack = []
    for line in fileinput.input(args.files):
        if args.strip:
            line=line.strip()
        line_stack.append(line)
        if len(line_stack) > 1 :
            if line_stack[0:1] == line_stack[-1:]:
                continue
            else:
                printer(line, args.strip)
                line_stack=line_stack[len(line_stack)-1:]
                duplicate_count = 0
        else:
            printer(line, args.strip)
        
        
