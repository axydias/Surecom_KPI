import sys
from os import listdir
from os.path import join
from Parser import Parser


# Read contents of inputDirPath and returns 2 lists: one with absolute names and one with relative names
def getInputFileList(inputDirPath):
    entries = listdir(inputDirPath)
    fmtFiles = []
    pureFilenamesList = []
    for e in entries:
        if e.lower().endswith(".fmt"):
            fmtFiles.append(join(inputDirPath, e))
            pureFilenamesList.append(e)
    return fmtFiles, pureFilenamesList


if __name__ == '__main__':

    # Check arguments
    if len(sys.argv) == 2:
        inputDir = sys.argv[1]
    else:
        print("Usage:" + sys.argv[0] + "input_directory_with_FMT_files")
        exit(1)

    # Read FMT files in input dir
    print("Program started")
    files, pureFilenames = getInputFileList(inputDir)
    print("Files to be processed: ")
    print(pureFilenames)

    # Parse files and create outputs
    for file in files:
        parser = Parser(file)
        parser.writeOutput()

    print("Program ended with success")
