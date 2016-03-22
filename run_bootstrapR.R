
library(class)
library(RWeka)


path = "C:\\Users\\flavio\\Desktop\\github\\"


shape = read.csv(paste(path,"shape_features.csv",sep = ""))
firstOrder_texture = read.csv(paste(path,"firstOrder_texture.csv",sep = ""))
glcm_isotopric = read.csv(paste(path,"glcm_isotropic.csv",sep = ""))

shape.first = cbind(shape[,1:dim(shape)[2] - 1], firstOrder_texture)
shape.first.glcm = cbind(shape.first[,1:dim(shape.first)[2] - 1], glcm_isotopric)


for (i in 1:dim(shape.first)[2]-1){
  name = paste0('V',as.character(i));
  colnames(shape.first)[i] <- name;
}
colnames(shape.first)[i+1] <- 'label';

for (i in 1:dim(shape.first.glcm)[2]-1){
  name = paste0('V',as.character(i));
  colnames(shape.first.glcm)[i] <- name;
}
colnames(shape.first.glcm)[i+1] <- 'label';


#normalize
shape = Normalize(~.,shape)
firstOrder_texture = Normalize(~.,firstOrder_texture)
glcm_isotropic = Normalize(~.,glcm_isotopric)
shape.first = Normalize(~.,shape.first)
shape.first.glcm = Normalize(~.,shape.first.glcm)


nboot = 500;

fm.shape = bootstrapR(data = shape,nBoot = nboot,classifier = 'svm',typeSVM = 'C-svc',kernelSVM = 'rbddot');
fm.firstOrder_texture = bootstrapR(data = firstOrder_texture,nBoot = nboot,classifier = 'svm',typeSVM = 'C-svc',kernelSVM = 'rbddot');
fm.glcm_isotropic = bootstrapR(data = glcm_isotropic,nBoot = nboot,classifier = 'svm',typeSVM = 'C-svc',kernelSVM = 'rbddot');
fm.shape.first = bootstrapR(data = shape.first,nBoot = nboot,classifier = 'svm',typeSVM = 'C-svc',kernelSVM = 'rbddot');
fm.shape.first.glcm = bootstrapR(data = shape.first.glcm,nBoot = nboot,classifier = 'svm',typeSVM = 'C-svc',kernelSVM = 'rbddot');


boxplot(c(fm.shape),c(fm.firstOrder_texture),c(fm.glcm_isotropic),
        c(fm.shape.first),c(fm.shape.first.glcm),at=c(1,2,3,4,5),main = "Boxplots Using SVM Classifier",
        xaxt='n', boxwex=0.25, staplewex=.5, ylim=c(0.73,1),ylab=expression(bold('F-Score')),
        xlab=expression(bold("Descriptors")),col=c('white','gray90','gray70','gray50','gray30'))
text(x=c(1.22,2.5,3.45,4.23,5.37),y=0.71,c('Shape [A]','First Order Texture [B]','Isotropic GLCM [C]','[A] + [B]','[A] + [B] + [C]'),adj=1, xpd=TRUE);

fs.shape = fScore_632(fm.shape,shape,nboot)
fs.firstOrder = fScore_632(fm.firstOrder_texture,firstOrder_texture,nboot)
fs.glcm = fScore_632(fm.glcm_isotropic,glcm_isotropic,nboot)
fs.shape.first = fScore_632(fm.shape.first,shape.first,nboot)
fs.shape.first.glcm = fScore_632(fm.shape.first.glcm,shape.first.glcm,nboot)

print("Shape F-Score: "); print(fs.shape)
print("First Order Texture F-Score: "); print(fs.firstOrder)
print("Isotropic GLCM F-Score: "); print(fs.glcm)
print("Shape + First Order Texture F-Score: "); print(fs.shape.first)
print("Shape + First Order Texture + GLCM F-Score: "); print(fs.shape.first.glcm)

