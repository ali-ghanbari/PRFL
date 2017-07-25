import os
import sys
import numpy as np
import pandas as pd
import time

class PageRanker:
    def __init__(self, paraDict):
        self.staticInfoPath = paraDict["staticInfoPath"]
        self.dynamicInfoPath = paraDict["dynamicInfoPath"]

        self.outputPath = paraDict["outputPath"]
        self.dampingFactor = float(paraDict["dampingFactor"])
        self.alpha = float(paraDict["alpha"])
        self.delta = float(paraDict["delta"])

        self.failingTestsFileName = os.path.join(self.staticInfoPath, "failing_tests.txt")
        self.methodCoverageFileName = os.path.join(self.dynamicInfoPath, "test_coverage.txt")
        self.staticCallGraphFileName = os.path.join(self.staticInfoPath, "call_graph.txt")

        self.failingTestList = list()
        self.testMethodDict = dict()
        self.methodTestDict = dict()
        self.staticCallGraphDict = dict()

        # define connection matrix
        self.failingCnnxMtrxDict = None
        self.passingCnnxMtrxDict = None
        self.failingMethodRankingVector = None
        self.passingMethodRankingVector = None


    # read failing tests from dataPath/failing_tests.txt
    def getFailingTestList(self):
        with open(self.failingTestsFileName, 'r') as file:
            for line in file:
                self.failingTestList.append(line.rstrip('\n'))
        print("    getFailingTestList DONE")


    # read method coverage (test-method mapping) from dataPath/test_coverage.txt
    def getTestMethodDict(self):
        with open(self.methodCoverageFileName, 'r') as file:
            for line in file:
                methodList = line.rstrip('\n').split("\t")
                testName = methodList[0]
                self.testMethodDict[testName] = methodList[1:]
        print("    getTestMethodDict DONE")


    # get method-test mapping from self.testMethodDict
    def getMethodTestDict(self):
        for test_i in self.testMethodDict:
            for method_j in self.testMethodDict[test_i]:
                if method_j not in self.methodTestDict:
                    self.methodTestDict[method_j] = list()
                self.methodTestDict[method_j].append(test_i)
        print("    getMethodTestDict DONE")


    # read static call graph (caller-callee mapping) from rootPath/StaticCallGraph
    def getStaticCallGraph(self):
        with open(self.staticCallGraphFileName, 'r') as file:
            for line in file:
                lineList = line.rstrip('\n').split("\t")
                caller = lineList[0]
                calleeList = lineList[1:]
                self.staticCallGraphDict[caller] = calleeList
        print("    getStaticCallGraph DONE")


    # get method to method matrices of failing/passing tests from dataPath/CoverageMatrix (these matrices are constructed based on Static Call Graph)
    def getCnnxDict(self):
        # test set
        allTestSet = set(self.testMethodDict.keys())
        failingTestSet = set(self.failingTestList)
        passingTestSet = allTestSet.difference(failingTestSet)

        # method set
        failingMethodSet = set()
        passingMethodSet = set()

        # assumes that all methods covered by failing tests are failing methods
        for test_i in failingTestSet:
            failingMethodSet = failingMethodSet.union(self.testMethodDict[test_i])
        # assumes that all methods covered by passing tests are passing methods
        for test_j in passingTestSet:
            passingMethodSet = passingMethodSet.union(self.testMethodDict[test_j])

        # get passing and failing connection matrices
        self.failingCnnxMtrxDict = self.getConnectionMatrix(failingMethodSet, failingTestSet, 1.0, "failing")
        self.passingCnnxMtrxDict = self.getConnectionMatrix(passingMethodSet, passingTestSet, 1.0, "passing")
        print("    getCnnxDict DONE")


    # (invoked by getBipartiteRanking) generate method-method, method-test and test-method connection
    def getConnectionMatrix(self, methodSet, testSet, returnWeight, mode):
        print ('        Constructing %s Matrix...' %('Passing' if mode == "passing" else 'Failing'))

        def getMatrix(inputList, inputDict, inputSet, inputSetList):
            listLen = len(inputList)
            setLen = len(inputSet)
            matrix = np.zeros((listLen, setLen))
            for index_i in range(listLen):
                list_element_i = inputList[index_i]
                list_element_i_covered_set = set(inputDict[list_element_i]).intersection(inputSet)
                list_element_i_covered_num = len(list_element_i_covered_set)
                list_element_i_weight = 1.0 / float(list_element_i_covered_num)
                index_j_list = [inputSetList.index(set_element_j) for set_element_j in list_element_i_covered_set]
                matrix[index_i, index_j_list] = list_element_i_weight
            return matrix

        # define method and test list
        methodList = list(methodSet)
        methodNum = len(methodList)
        testList = list(testSet)
        testNum = len(testList)
        prime_M2Mmatrix = np.zeros((methodNum, methodNum)) # call
        prime_M2Mmatrix_return = np.zeros((methodNum, methodNum)) # return

        # methodList is failingMethodSet
        for method_i in methodList:
            if method_i in self.staticCallGraphDict:
                caller_index = methodList.index(method_i)
                # only consider failing callees 
                callee_index_list = [methodList.index(i) for i in self.staticCallGraphDict[method_i] if i in methodList]
                prime_M2Mmatrix[caller_index, callee_index_list] = 1.0
                prime_M2Mmatrix_return[callee_index_list, caller_index] = 1.0

        # assumes that all methods are mutually recursive!
        M2Mmatrix = prime_M2Mmatrix + prime_M2Mmatrix_return * self.delta

        # construct M2Tmatrix
        M2Tmatrix = getMatrix(methodList, self.methodTestDict, testSet, testList)

        # construct T2Mmatrix
        T2Mmatrix = getMatrix(testList, self.testMethodDict, methodSet, methodList)

        # return connection matrix
        cnnxMtrxDict = dict()
        cnnxMtrxDict["methodList"] = methodList
        cnnxMtrxDict["testList"] = testList
        cnnxMtrxDict["M2Mmatrix"] = M2Mmatrix # column-normalized?
        cnnxMtrxDict["M2Tmatrix"] = M2Tmatrix
        cnnxMtrxDict["T2Mmatrix"] = T2Mmatrix
        return cnnxMtrxDict


    def getBipartiteRanking(self):
        self.failingMethodRankingVector = self.getStationaryRanking(self.failingCnnxMtrxDict, True)
        self.passingMethodRankingVector = self.getStationaryRanking(self.passingCnnxMtrxDict, False)
        print ("    getBipartiteRanking DONE")


    def getStationaryRanking(self, cnnxMtrxDict, falseFlag):

        def getTestCaseWeight(T2Mmatrix):
            [rows, cols] = T2Mmatrix.shape
            weightArray = np.zeros((rows, 1))
            for i in range(rows):
                weightArray[i, 0] = 1.0 / np.sum(T2Mmatrix[i, :])
                # weightArray[i, 0] = np.exp(-1 * np.sum(T2Mmatrix[i, :]))
            normailzedWeightArray = weightArray / np.sum(weightArray)
            return normailzedWeightArray

        MMt = np.transpose(cnnxMtrxDict["M2Mmatrix"])
        Y = np.transpose(cnnxMtrxDict["T2Mmatrix"])
        Xt = np.transpose(cnnxMtrxDict["M2Tmatrix"])

        if falseFlag is True:
            teleportionVector = getTestCaseWeight(cnnxMtrxDict["T2Mmatrix"])
        else:
            teleportionVector = np.ones((len(cnnxMtrxDict["testList"]), 1)) / float(len(cnnxMtrxDict["testList"]))

        methodRankingVector = np.ones((len(cnnxMtrxDict["methodList"]), 1)) / float(len(cnnxMtrxDict["methodList"]) + len(cnnxMtrxDict["testList"]))
        testRankingVector = np.ones((len(cnnxMtrxDict["testList"]), 1)) / float(len(cnnxMtrxDict["methodList"]) + len(cnnxMtrxDict["testList"]))
        dampingFactor = self.dampingFactor
        alpha = self.alpha

        for i in range(25):
            updatedMethodRankingVector = dampingFactor * (np.dot(Y, testRankingVector) + alpha * np.dot(MMt, methodRankingVector))
            updatedTestRankingVector = dampingFactor * np.dot(Xt, methodRankingVector) + (1.0 - dampingFactor) * teleportionVector
            methodRankingVector = updatedMethodRankingVector / np.amax(updatedMethodRankingVector)
            testRankingVector = updatedTestRankingVector / np.amax(updatedTestRankingVector)

        normalizedMethodRankingVector = methodRankingVector / np.amax(methodRankingVector)
        return normalizedMethodRankingVector


    def generateAndSaveResult(self):
        # suspicious methods are those covered by failing test cases
        suspiciousMethodNum = len(self.failingCnnxMtrxDict["methodList"])
        # result matrix: columns =>
        # 0. PageRank_failing_score
        # 1. PageRank_passing_score
        # 2. number of failing tests
        # 3. number of passing tests
        # 4. number of total failing tests
        # 5. number of total passing tests
        resultMtrx = np.zeros((suspiciousMethodNum, 6))

        for method_i in self.failingCnnxMtrxDict["methodList"]:
            method_index = self.failingCnnxMtrxDict["methodList"].index(method_i)

        # 0. pr_failing_score
            resultMtrx[method_index, 0] = self.failingMethodRankingVector[method_index, 0]

        # 1. pr_passing_score
            if method_i not in self.passingCnnxMtrxDict["methodList"]:
                resultMtrx[method_index, 1] = 0.0
            else:
                temp_index = self.passingCnnxMtrxDict["methodList"].index(method_i)
                resultMtrx[method_index, 1] = self.passingMethodRankingVector[temp_index, 0]

        # 2. # of failing tests
            ttlTestNum = len(self.methodTestDict[method_i])
            failingTestNum = len(set(self.failingTestList).intersection(self.methodTestDict[method_i]))
            passingTestNum = ttlTestNum - failingTestNum
            resultMtrx[method_index, 2] = failingTestNum

        # 3. # of passing tests
            resultMtrx[method_index, 3] = passingTestNum

        # 4. # of total failing tests
            resultMtrx[method_index, 4] = len(self.failingTestList)

        # 5. # of total passing tests
            resultMtrx[method_index, 5] = len(self.testMethodDict.keys()) - len(self.failingTestList)


        outputFileName = os.path.join(self.outputPath, "PageRank_scores.csv")
        colNames = ["failing_score", "passing_score", "#failing", "#passing", "#TTLfailing", "#TTLpassing"]
        df = pd.DataFrame(resultMtrx, columns=colNames, index=self.failingCnnxMtrxDict["methodList"])
        df.to_csv(outputFileName, sep=',', encoding='utf-8', float_format="%5.8f")


if __name__ == "__main__":
    paraDict = dict()
    paraDict["staticInfoPath"] = sys.argv[1]
    paraDict["dynamicInfoPath"] = sys.argv[2]
    paraDict["outputPath"] = sys.argv[3]
    paraDict["dampingFactor"] = sys.argv[4]
    paraDict["alpha"] = sys.argv[5]
    paraDict["delta"] = sys.argv[6]

    pr = PageRanker(paraDict)
    pr.getFailingTestList()
    pr.getTestMethodDict()
    pr.getMethodTestDict()
    pr.getStaticCallGraph()
    pr.getCnnxDict()
    pr.getBipartiteRanking()
    pr.generateAndSaveResult()


