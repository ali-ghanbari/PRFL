# CONFIG
# parameters
damping_factor=0.7
alpha=0.001
delta=1.0

# directories
codeDir=./code
subjectDir=./example
jarDir=$codeDir/callgraphanalysis/build/jar/
dynamic_infoDir=$subjectDir/dynamic_info
outputDir=./output


# RUN
rm -rf $outputDir
mkdir -p $outputDir

echo "Collecting failing tests..."
python $codeDir/getFailingTests.py $subjectDir $outputDir

echo "Constructing static call graph..."
python $codeDir/getCallGraph.py $jarDir $subjectDir $outputDir

echo "Executing PageRank..."
python $codeDir/runPageRank.py $outputDir $dynamic_infoDir $outputDir $damping_factor $alpha $delta

echo "Ranking..."
python $codeDir/rankMethods.py $outputDir $outputDir