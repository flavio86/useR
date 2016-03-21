'
Script to run the bootstrap classification methodology
input:
  data -> the dataset has to follow this: [atr1 atr2 atr3 ... atrn label], each line is one sample
  nboot -> the number of datasets that will be generated from the original dataset
  classifier -> {svm,knn} (you can put more classifiers)
  IR -> {0,1} if 0 do not use the irformation ratio to erase irrelevant attributes, 1 otherwise
  typeSVM -> see kernlab library to use other types
  kernelSVM -> see kernlab library to use other types
  knn -> K of knn
output:
  F-score of the nboot datasets
'
bootstrapR <- function (data, nBoot=50,classifier='svm',IR=0,typeSVM = 'C-svc',kernelSVM = 'rbfdot',knn = 9){
  library(kernlab)
  library(class)
  ##pre-processing, remove irrelevant features
  if(IR == 1){
    gR = gainRatio(data);
    print(gR);
    notZeros = (gR!=0);
    cont=1;
    d <-  matrix(0,dim(data)[1],sum(gR!=0));
    for (zeros in 1:length(notZeros)){
      if (notZeros[zeros] == TRUE){
        d[,cont] = data[,zeros];
        cont = cont+1;
      }
    }
    
    d = cbind(d,data[,dim(data)[2]]);
    data = d;
    print(sum(gR == 0)); 
  }
  
  d = data;
  a <- dim(data)[1];
  b <- dim(data)[2];
  nVar <- dim(data)[2]-1;
  todos <- c(1:a);
  fm <-  matrix(0,nBoot);
  
  for (j in 1:nBoot){
    print(paste("BOOT: ",j))
    #training set
    posicoes <- sample(1:a,a,replace = TRUE);
    xTrain <- data[posicoes,1:nVar];
    yTrain <- data[posicoes,nVar+1];
    
    #test set
    posicoes2 <- setdiff(todos,posicoes);
    xTest <- data[posicoes2,1:nVar];
    yTest <- data[posicoes2,nVar+1];
    #print(data.frame(yTrain))
    #print (dim(xTrain))
    #print (dim(data.frame(yTrain)))
    if (classifier == 'knn'){
      pred<-knn(data.frame(xTrain), data.frame(xTest), yTrain, knn);
    }else if (classifier == 'svm'){
      svm.model = ksvm(data.matrix(xTrain),data.matrix(yTrain),type = typeSVM)
      pred = predict(svm.model,xTest)
    }
    #statistical
    matriz_de_confusao = table(pred,yTest);
    VP = matriz_de_confusao[1,1];
    VN = matriz_de_confusao[2,2];
    FP = matriz_de_confusao[1,2];
    FN = matriz_de_confusao[2,1];
    p1 = VP/(VP + FP)
    r1 = VP/(VP + FN)
    p2 = VN/(VN + FN)
    r2 = VN/(VN + FP)
    fm1 = 2*(p1*r1)/(p1+r1);
    fm2 = 2*(p2*r2)/(p2+r2);
    fm[j] = (fm1+fm2)/2;
  }
  return (fm);
}
  
  