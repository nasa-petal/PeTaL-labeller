# PeTaL (Periodic Table of Life) Labeller

The Periodic Table of Life (PeTaL, pronounced petal) is a design tool aimed at allowing users to seemlesly move from ideas (from nature or other sources) to design.

PeTaL is comprised of multiple interconnected services. This repository is for the Labeller. There are other repositories for the [API and database](https://github.com/nasa/petal-db), and [ReactJS web front end client](https://github.com/nasa/PeTaL).

## Getting Started

The labeler is currently in a prototype stage and we are experimenting with different models, currently transformer-based models (BERT, XLNet, BioBERT) and support vector machines (SVMs).

## Deploying the SciBERT model to Sagemaker

Generate a model file `last_saved.pth` and store in `auto-labeler/scibert/sagemaker/`

Replace X.X with the next version numbers ex. 0.1 to 0.2.

`cd auto-labeler/scibert/sagemaker`

Run `tar -cvzf scibert-X.X-model.tar.gz code last_saved.pth` to generate a tarball.

Upload tarball to `s3://petal-bucket`

For more information about the model format Sagemaker expects see:
https://sagemaker.readthedocs.io/en/stable/frameworks/pytorch/using_pytorch.html#model-directory-structure

For more information about deploying a model trained outside of Sagemaker to Sagemaker see:
https://sagemaker.readthedocs.io/en/stable/frameworks/pytorch/using_pytorch.html#bring-your-own-model

### Transformers

Notable Papers:
- [Attention is All You Need](https://arxiv.org/abs/1706.03762)
- [BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding](https://arxiv.org/abs/1810.04805)

The transformer architecture consists of a stack twelve encoders and decoders that carry different weights. The encoders consist of a self-attention layer and feed-forward neural network layer that pass embeddings through as vectors, as well as softmax and linear transformation layers to give its output probabilities. The self-attention layer mechanisms operate to have each word analyze its surrounding words to see how a specific word relates to the rest of the sentence and its contextual meaning at a sentence level, using those emeddings passed through.

[BERT](https://arxiv.org/abs/1810.04805) (Bidirectional Encoder Representations from Transformers) is a pre-trained transformer model that contains 12 (or 24) encoders in its stack, and using transfer learning to fine-tune it specifically to our dataset and biomimicry taxonomy.
It specifically allows for better understanding of contextual meaning within the articles, since it uses a masked language model through semi-supervised sequence learning to derive context and semantics from surrounding words. BERT's architecture contains larger feed-forward networks and more attention heads as it was pretrained on a large corpus of unlabelled text including BookCorpus, consisting of 800 million words, and a version of Wikipedia, consisting of over 2.5 billion words. It distinguishes between sentences through its use of masked language modeling (MLM) and next sentence predictions (NSP).

To implement our transformer models, we used the [Huggingface transformers library](https://huggingface.co/transformers/) with a PyTorch implementation. For this text classification task, it is necessary to alter the pre-trained BERT model specifically for classification, so using the HuggingFace PyTorch implementation for BERT, we implemented the `BertForSequenceClassification` class that contains a single layer for linear classification. In addition, the training loop consisted of training and validation phases with a forward pass, backpropagation, variable tracking, loss computation, and optimization using the `AdamW` optimizer. The optimizer hyperparameters consisted of a batch size of 32, learning rate of 2e-5, and four training epochs.
