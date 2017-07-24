import os
import sys


def runCMD(jarFolder, subjFolder, outputFolder):
    jar = os.path.join(jarFolder, "CallgraphAnalysis.jar")
    classFolder = os.path.join(subjFolder, "target", "classes")
    outputFile = os.path.join(outputFolder, "call_graph.txt")
    cmd = "java -jar %s %s > %s" %(jar, classFolder, outputFile)
    os.system(cmd)


if __name__ == "__main__":
    jarFolder = sys.argv[1]
    subjFolder = sys.argv[2]
    outputFolder = sys.argv[3]
    runCMD(jarFolder, subjFolder, outputFolder)
