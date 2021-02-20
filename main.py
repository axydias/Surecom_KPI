import sys
from os import listdir
from os.path import join
from Parser import Parser


def getInputFileList(inputDir):
    entries = listdir(inputDir)
    fmtFiles = []
    pureFilenames = []
    for e in entries:
        if e.lower().endswith(".fmt"):
            fmtFiles.append(join(inputDir,e))
            pureFilenames.append(e)
    return fmtFiles, pureFilenames


if __name__ == '__main__':

    if len(sys.argv) == 2:
        inputDir = sys.argv[1]
    else:
        print("Usage:" + sys.argv[0] + "input_directory")
        exit(1)

    print("Program started")
    files, pureFilenames = getInputFileList(inputDir)
    print("Files to be processed: ")
    print(pureFilenames)

    for file in files:
        parser = Parser(file)
        parser.writeOutput()
    print("Program ended with success")
