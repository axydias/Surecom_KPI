import sys
from Parser import Parser

if __name__ == '__main__':

    if len(sys.argv) == 2:
        path = sys.argv[1]
    else:
        print("Usage:" + sys.argv[0] + "input_directory")
        exit(1)

    print("Program started")
    parser = Parser('input/VF BMT Car pk UMTS.FMT')
    parser.writeOutput()
    print ("Program ended with success")
