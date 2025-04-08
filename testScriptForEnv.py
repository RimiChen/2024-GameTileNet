import torch
torch.cuda.is_available()

x = torch.rand(5, 3)
print(x)


###
import numpy
print('The numpy version is {}.'.format(numpy.__version__))

##
import nltk
import sklearn

print('The nltk version is {}.'.format(nltk.__version__))
print('The scikit-learn version is {}.'.format(sklearn.__version__))

##
import pandas as pd

print("The panda version is {}.".format(pd.__version__))

##
import matplotlib
print('matplotlib: {}'.format(matplotlib.__version__))

## 
import seaborn as sns
print('seaborn: {}'.format(sns.__version__))