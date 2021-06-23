## is-biom.csv

Training dataset used in SageMaker Studio to run an AutoML experiment to train and optimize a binary classification model (Y/N biomimicry).

## multilabel-for-comprehend

Training dataset used in AWS Comprehend to train and optimize a multi-label text classification model. Amazon Comprehend can only handle up to 100 distinct labels. Each label has to be applied to at least 10 papers. Our full taxonomy includes 130 labels, but only 100 leaf labels. This dataset only includes leaf labels that are applied to a minimum of 10 papers in the first column. The second column is the title + abstract of the paper.