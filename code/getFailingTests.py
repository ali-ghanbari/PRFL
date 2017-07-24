import os
import sys
import glob
import xml.etree.cElementTree as ET


def getFailingTests(subjFolder):
    failingTestList = []
    targetFolder = os.path.join(subjFolder, "target", "surefire-reports")
    fileList = glob.glob(os.path.join(targetFolder, "*.xml"))
    failingFileSet = set()

    for file_i in fileList:
        tree = ET.ElementTree(file=file_i)
        for elem in tree.iter():
            if elem.tag == "testcase":
                for child_i in elem:
                    if child_i.tag == "failure" or child_i.tag == "error":
                        className = elem.attrib["classname"]
                        methodName = elem.attrib["name"]
                        failingTestList.append(".".join([className, methodName]))   
                        failingFileSet.add(file_i.replace(subjFolder, ""))
    return failingTestList, failingFileSet


def saveResult(subjFolder, outputFolder, failingTestList, failingFileSet):
    outputFile1 = os.path.join(outputFolder, "failing_tests.txt")

    with open(outputFile1, "w+") as file:
        for test_i in failingTestList:
            file.write(test_i + "\n")

    outputFile2 = os.path.join(outputFolder, "info.txt")
    with open(outputFile2, "w+") as file:
        file.write("XML files with failing tests:\n")
        file.write("\tSUBJECT_DIR=" + os.path.abspath(subjFolder) + "\n")
        for failingFile_i in failingFileSet:
            file.write("\t$SUBJECT_DIR" + failingFile_i + "\n")
        file.write("\n")


if __name__ == "__main__":
    subjFolder = sys.argv[1]
    outputFolder = sys.argv[2]
    failingTestList, failingFileSet = getFailingTests(subjFolder)
    saveResult(subjFolder, outputFolder, failingTestList, failingFileSet)

