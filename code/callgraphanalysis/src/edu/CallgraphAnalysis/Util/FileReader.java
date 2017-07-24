package edu.CallgraphAnalysis.Util;

import java.io.File;
import java.util.ArrayList;
import java.util.List;


public class FileReader {
    public static List<String> getList(String[] args) {

//        check argument number
        if (args.length != 1){
            System.err.println("The argument should be a folder includes all class files.");
            return null;
        }

        File f = new File(args[0]);

        if (!f.exists()) {
            System.err.println("Folder" + args[0] + " does not exist.");
            return null;
        }
        else if(!f.isDirectory()){
            System.err.println("The input " + args[0] + " is not a folder.");
            return null;
        }

        List<String> fileList = new ArrayList<>();
        getFilesFromPath(args[0], fileList);
        return fileList;
    }


    public static void getFilesFromPath(String classFolderPath, List<String> fileList){
        File directory = new File(classFolderPath);
        File[] fList = directory.listFiles();

        for (File file : fList) {
            if (file.isFile() && file.getName().endsWith(".class")) {
                fileList.add(file.getAbsolutePath());
            } else if (file.isDirectory()) {
                getFilesFromPath(file.getAbsolutePath(), fileList);
            }
        }
    }


}
