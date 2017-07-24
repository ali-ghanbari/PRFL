# PRFL #

A tool for boosting spectrum-based fault localization using PageRank.

## Tool ##

**PRFL** is mainly implemented in Python and the source code lies in folder `./code`. **PRFL** uses the following dependencies:

- Numpy
- Pandas

These packages can be installed by `sudo pip install`.

The static callgraph extractor is implemented in Java. Before executing `run.sh`, please install this module following the instruction under folder `./code/callgraphanalysis`

Currently, the tool for dynamic analysis is not provided, and please use other third-party tools to collect coverage information. The format of dynamic coverage is
```
test_1    method_1    method2    method3    ...
test_2    method_1    method3    method5    ...
test_3    method_2    method4    method5    ...
...
```

## Getting started ##
In folder `./example`, we provide a Java project ([commons-lang](https://github.com/apache/commons-lang), [Defects4J](https://github.com/rjust/defects4j) ID: 7b) to test **PRFL**, and the faulty method is
```
org.apache.commons.lang3.math.NumberUtils:createNumber(Ljava/lang/String;)Ljava/lang/Number;
```

This project has been compiled and tested, the class files and test reports lie in `./example/target/classes` and `./example/target/surefire-reports`, respectively.
The dynamic coverage information is under `./example/dynamic_info`.

Parameters and directories can be set up in `run.sh` and the boosted SBFL rank list is under folder `./output/pr_ranking`.

## Publication ##
Zhang, Mengshi, Xia Li, Lingming Zhang, and Sarfraz Khurshid. "Boosting spectrum-based fault localization using PageRank." In Proceedings of the 26th ACM SIGSOFT International Symposium on Software Testing and Analysis, pp. 261-272. ACM, 2017.

## Bibtex ##
```
@inproceedings{zhang2017boosting,
  title={Boosting spectrum-based fault localization using PageRank},
  author={Zhang, Mengshi and Li, Xia and Zhang, Lingming and Khurshid, Sarfraz},
  booktitle={Proceedings of the 26th ACM SIGSOFT International Symposium on Software Testing and Analysis},
  pages={261--272},
  year={2017},
  organization={ACM}
}
```
