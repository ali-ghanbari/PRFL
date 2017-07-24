package edu.CallgraphAnalysis;

import edu.CallgraphAnalysis.Util.FileReader;

import java.util.List;

public class JCallGraph {
    public static void main(String[] args) {
        List<String> fileList = FileReader.getList(args);
        if (fileList == null){
            return;
        }
        else{
//            for (String i : fileList){
//                System.out.println(i);
//            }

            CallgraphConstructor cgConstructor = new CallgraphConstructor(fileList);
            cgConstructor.constructPackageSet();
            cgConstructor.constructCallGraph();
            cgConstructor.refineCallgraph();
            cgConstructor.printCallgraph();
        }
    }
}
