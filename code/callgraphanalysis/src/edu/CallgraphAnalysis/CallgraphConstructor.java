package edu.CallgraphAnalysis;

import java.io.FileInputStream;
import java.util.*;

import org.objectweb.asm.*;
import org.objectweb.asm.tree.*;
import org.objectweb.asm.util.*;


public class CallgraphConstructor {
    private List<String> fileList;
    private Set<String> packageSet;
    private Map<String, Set<String>> callgraphDict;

//    format: class -> Set<Method>
    private Map<String, Set<String>> classMethodDict;

//    format superclass -> Set<subclass>
    private Map<String, Set<String>> inheritDict;


    public CallgraphConstructor(List<String> fileList){
        this.fileList = fileList;
        this.packageSet = new HashSet<>();
        this.callgraphDict = new HashMap<>();
        this.classMethodDict = new HashMap<>();
        this.inheritDict = new HashMap<>();
    }


    public void constructPackageSet(){
        try{
            for (String file_i : fileList) {
                FileInputStream in = new FileInputStream(file_i);
                ClassNode classNode = new ClassNode();
                ClassReader classReader = new ClassReader(in);
                classReader.accept(classNode, 0);

                List<String> wordList = Arrays.asList(classNode.name.split("/"));
                String packageName = String.join(".", wordList.subList(0, (wordList.size()-1)));
                this.packageSet.add(packageName);
            }

        } catch (Exception e){
            System.err.println(e);
        }
    }


    public void constructCallGraph(){
        try{
            for (String file_i : this.fileList){
                FileInputStream in = new FileInputStream(file_i);
                ClassNode classNode = new ClassNode();
                ClassReader classReader = new ClassReader(in);
                classReader.accept(classNode, 0);
                String callerClassName = classNode.name.replace('/', '.');

//                check if class name is in classMethodDict
                if (!this.classMethodDict.containsKey(callerClassName)){
                    this.classMethodDict.put(callerClassName, new HashSet<>());
                }

//                check if class has a superclass
                List<String> superNameWordList = Arrays.asList(classNode.superName.split("/"));
                String superPkgName = String.join(".", superNameWordList.subList(0, (superNameWordList.size()-1)));
                String superClassName = classNode.superName.replace('/', '.');
                if (this.packageSet.contains(superPkgName)){
                    if(!this.inheritDict.containsKey(superClassName)){
                        this.inheritDict.put(superClassName, new HashSet<>());
                    }
                    this.inheritDict.get(superClassName).add(callerClassName);
                }

//                check all methods
                List<MethodNode> methodList = classNode.methods;
                for (MethodNode method_i : methodList) {
                    InsnList inst_j = method_i.instructions;
                    String callerMethodName = method_i.name + method_i.desc;
                    String callerFullName = callerClassName + ":" + callerMethodName;
                    this.classMethodDict.get(callerClassName).add(callerMethodName);

                    ListIterator insnIter = inst_j.iterator();
                    while (insnIter.hasNext()){
                        Object obj = insnIter.next();
                        if (obj instanceof MethodInsnNode){
                            MethodInsnNode mInsnNode = (MethodInsnNode)obj;
                            String calleeClassName = mInsnNode.owner;
                            String calleeMethodName = mInsnNode.name + mInsnNode.desc;
                            String calleeFullName = calleeClassName.replace('/', '.') + ":" + calleeMethodName;

//                          check if callee belongs target projects
                            List<String> wordList = Arrays.asList(calleeClassName.split("/"));
                            String calleePkgName = String.join(".", wordList.subList(0, (wordList.size()-1)));

                            if (this.packageSet.contains(calleePkgName)){
//                             this.callgraph does not include callerFullName, add it
                                if (!this.callgraphDict.containsKey(callerFullName)){
                                    this.callgraphDict.put(callerFullName, new HashSet<>());
                                }
                                this.callgraphDict.get(callerFullName).add(calleeFullName);
                            }
                        }
                    }
                }
            }
        } catch (Exception e){
            System.out.println(e);
        }
    }


    public void refineCallgraph(){
//        check all overwritten methods
//        format: superMathod -> Set<subMethod>
        Map<String, Set<String>> owMethodDict = new HashMap<>();
        
        for (String superClass_i : this.inheritDict.keySet()){
            for (String subClass_j : this.inheritDict.get(superClass_i)){
                Set<String> superMethodSet = this.classMethodDict.get(superClass_i);
                Set<String> subMethodSet = this.classMethodDict.get(subClass_j);

                if ((superMethodSet != null) && (subMethodSet != null)){                  
                    Set<String> intersectionMethods = new HashSet<>(superMethodSet);
                    intersectionMethods.retainAll(subMethodSet);

                    if (!intersectionMethods.isEmpty()) {
                        for (String method_i : intersectionMethods){
                            String superMethod = superClass_i + ":" + method_i;
                            String subMethod = subClass_j + ":" + method_i;
                            if (!owMethodDict.containsKey(superMethod)){
                                owMethodDict.put(superMethod, new HashSet<>());
                            }
                            owMethodDict.get(superMethod).add(subMethod);
                        }
                    }
                }
            }
        }

//        check if any super class methods are called
        for (String callerMethod : this.callgraphDict.keySet()){
            if (owMethodDict.containsKey(callerMethod)){
                Set<String> subMethodSet = owMethodDict.get(callerMethod);
                this.callgraphDict.get(callerMethod).addAll(subMethodSet);
            }
        }
    }


    public Map<String, Set<String>> getCallgraph(){
        return this.classMethodDict;
    }

    public void printCallgraph(){
        for (String caller : this.callgraphDict.keySet()){
            System.out.print(caller);
            for (String callee : this.callgraphDict.get(caller)){
                System.out.print("\t" + callee);
            }
            System.out.println();
        }
    }
}
