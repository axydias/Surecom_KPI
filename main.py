import sys
from os import listdir
from Parser import Parser
from Bands import Operators
from Settings import OUTPUTDIR
from os.path import join, dirname, isdir
from os import mkdir


# Read contents of inputDirPath and returns 2 lists: one with absolute names and one with relative names
def getInputFileList(inputDirPath, filetype=".fmt"):
    entries = listdir(inputDirPath)
    fmtFiles = []
    pureFilenamesList = []
    for e in entries:
        if e.lower().endswith(filetype):
            fmtFiles.append(join(inputDirPath, e))
            pureFilenamesList.append(e)
    return fmtFiles, pureFilenamesList


def mergeOperationFunction(inputDirPath, mergeFilename_merge):
    print("Merging operation started")
    files_merge, pureFilenames_merge = getInputFileList(inputDirPath, ".csv")
    print("Files to be merged: ")
    print(pureFilenames_merge)
    # Create output dir if not exists
    if not isdir(join(dirname(__file__), OUTPUTDIR)):
        mkdir(join(dirname(__file__), OUTPUTDIR))
        print("Created directory: " + join(dirname(__file__), OUTPUTDIR))

    fullOutputFilename = join(dirname(__file__), join(OUTPUTDIR, mergeFilename_merge))
    with open(fullOutputFilename, 'w') as mergefile:
        for file in files_merge:
            with open(file) as infile:
                contents = infile.read()
                mergefile.write(contents)
                mergefile.write("\n")
    print("Created merged file: " + fullOutputFilename)
    print("Merging operation ended with success")


if __name__ == '__main__':

    # Check arguments
    if len(sys.argv) == 2:
        inputDir = sys.argv[1]
        mergeOperation = False
    else:
        if len(sys.argv) == 4 and sys.argv[2] == "--merge":
            inputDir = sys.argv[1]
            mergeFilename = sys.argv[3]
            mergeOperation = True
        else:
            print("Usage:" + sys.argv[0] + "input_directory_with_FMT_files")
            exit(1)

    # Check if merging operation is True
    if mergeOperation:
        mergeOperationFunction(inputDir, mergeFilename)
        exit(0)

    # Choose operator
    operator_to_scan = 0
    while operator_to_scan < 1 or operator_to_scan > len(Operators):
        print("Choose operator to scan frequencies:")
        i = 1
        for op in Operators:
            print(str(i) + ". " + op)
            i += 1
        operator_to_scan = input("Choose: ")
        operator_to_scan = int(operator_to_scan)

    print("You have selected to scan: " + Operators[operator_to_scan-1])

    # Read FMT files in input dir
    print("Program started")
    files, pureFilenames = getInputFileList(inputDir)
    print("Files to be processed: ")
    print(pureFilenames)

    # Parse files and create outputs
    for file in files:
        parser = Parser(file, operator_to_scan-1)
        parser.writeOutput()

    mergeOperationFunction(OUTPUTDIR, "merged.csv")
    print("Program ended with success")
