
fScore_632 <-function(fs,data,nBoot){
  
  nVar <- dim(data)[2]-1;
  x = as.matrix(data[,1:nVar])
  y = as.matrix(data[,nVar+1],drop=FALSE)
  svm.model = ksvm(x,y,type = "C-svc",kernel = "rbfdot")
  pred = predict(svm.model,x)
  
  confusion_matrix = table(pred,data[,nVar+1]);
  TP = confusion_matrix[1,1];
  TN = confusion_matrix[2,2];
  FP = confusion_matrix[1,2];
  FN = confusion_matrix[2,1];
  p1 = TP/(TP + FP)
  r1 = TP/(TP + FN)
  p2 = TN/(TN + FN)
  r2 = TN/(TN + FP)
  fm1 = 2*(p1*r1)/(p1+r1);
  fm2 = 2*(p2*r2)/(p2+r2);
  f = (fm1+fm2)/2;
  #############################################
  f632 = 0.368*f+(0.632/nBoot)*sum(fs);
  return (f632);
}

