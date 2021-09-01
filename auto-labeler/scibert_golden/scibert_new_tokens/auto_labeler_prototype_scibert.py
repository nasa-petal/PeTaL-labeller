'''
    Auto_labeler_scibert - this code trains the model on a single label csv data provided by Colleen and Alex
        Procedure:
            - Reads data and splits it into test train. Data is saved into dataset.pt
            - dataset.pt is read and loaded into dataloaders where it is sent to the training code
            - 
    Authors: Paht Juangphanich (paht.juangphanich@nasa.gov)
'''
import os
import argparse
from pathlib import Path
import torch, gdown
import pandas as pd
import numpy as np
from transformers import AutoTokenizer
from torch.utils.data import TensorDataset, random_split
from torch.utils.data import DataLoader, RandomSampler, SequentialSampler
from train import train
from nltk.tokenize import word_tokenize

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def get_args_parser():
    def str2bool(v):
        if isinstance(v, bool):
            return v
        if v.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif v.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')
    parser = argparse.ArgumentParser('Set SuperResolution GANS', add_help=False)
    parser.add_argument('--lr', default=1e-4, type=float)    
    parser.add_argument('--batch_size', default=32, type=int)
    parser.add_argument('--num_workers', default=4, type=int)
    parser.add_argument('--epochs', default=500, type=int)
    parser.add_argument('--validation_epoch', default=1, type=int, help='At what epoch do we run the validation')
    parser.add_argument('--output_dir',default='epochs',type=str, help='folder where to save checkpoints')
    return parser
    
def setup_dataset():
    """Setup the Train and Validation datasets

    Returns:
        (tuple): tuple containing:

            - **train_dataset** (torch.utils.data.TensorDataset): pitch distribution
            - **val_dataset** (torch.utils.data.TensorDataset): pitch to chord distribution
    """
    filename = 'SINGLELABEL_Colleen_and_Alex_training_data_4.19.csv'
    if (not os.path.exists(filename)):
        url = 'https://drive.google.com/file/d/1eOLNOl6ZMz4UxQ7qbSI-bJSSNkmNZjr9/view?usp=sharing'
        gdown.download(url, filename, quiet=False)
        md5 = 'fa837a88f0c40c513d975104edf3da17'
        gdown.cached_download(url, filename, md5=md5, postprocess=gdown.extractall)

    df = pd.read_csv(filename)
    df = df[['title', 'abstract', 'labels', 'doi', 'url', 'single_labels', 'labels_string']]
    df = df[df['single_labels'].notnull()]

    labels = []
    docs = []
    labels_test = []
    docs_test = []
    labels_dict = ["'Protect from harm'", "'Process resources'", "'Sense send or process information'", "'Maintain structural integrity'", "'Move'", "'Attach'", "'Maintain ecological community'", "'Chemically modify or Change energy state'", "'Change size or color'", "'Physically assemble/disassemble'"]

    single_labels = df["single_labels"].tolist()
    abstract = df["abstract"].tolist()
    title = df["title"].tolist()
    for i in range(len(title)):
        if i < len(title) - 40:
            docs.append(abstract[i])
            labels.append(labels_dict.index(single_labels[i]))
        else:
            docs_test.append(abstract[i])
            labels_test.append(labels_dict.index(single_labels[i]))

    print("Number of training labels: {:}".format(len(labels)))
    print("Number of training docs: {:}".format(len(docs)))
    print("Number of test labels: {:}".format(len(labels_test)))
    print("Number of test docs: {:}".format(len(docs_test)))
    
    regular_list = [word_tokenize(a) for a in abstract]
    tokens_flat = [item for sublist in regular_list for item in sublist]

    tokenizer = AutoTokenizer.from_pretrained("allenai/scibert_scivocab_uncased")
    tokenizer.add_tokens(tokens_flat)

    print('SciBERT tokenizer loaded')

    # original abstract
    print(' Original: ', docs[5])
    # abstract split into tokens
    print('Tokenized: ', tokenizer.tokenize(docs[5]))
    # abstract as mapped to ids
    print('Token IDs: ', tokenizer.convert_tokens_to_ids(tokenizer.tokenize(docs[5])))
   
    # Finishing tokenizing all docs and map tokens to thier word IDs
    input_ids = []
    attention_masks = []
    actual_labels_test = []

    for d in docs:
        encoded_dict = tokenizer.encode_plus(
                            d,                      
                            truncation=True,
                            add_special_tokens = True, 
                            max_length = 256,           
                            pad_to_max_length = True,
                            return_attention_mask = True,   
                            return_tensors = 'pt',     
                    )
        input_ids.append(encoded_dict['input_ids'])
        attention_masks.append(encoded_dict['attention_mask'])

    # Convert the lists into tensors.
    input_ids = torch.cat(input_ids, dim=0)
    attention_masks = torch.cat(attention_masks, dim=0)
    labels = torch.tensor(labels)

    print('Original: ', docs[5])
    print('Token IDs:', input_ids[5])
    print('Reverse:', tokenizer.convert_ids_to_tokens(input_ids[5]))

    # Split up training & testing/validation
    dataset = TensorDataset(input_ids, attention_masks, labels)

    # Number of docs to include per set
    train_size = int(0.9 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
    return train_dataset, val_dataset, tokenizer

def main(args:argparse.ArgumentParser): 
    """Runs the training loop
       
       [HuggingFace documentation](https://huggingface.co/transformers/v2.2.0/model_doc/bert.html)
    Args:
        args (argparse.ArgumentParser): [description]
    """
    # Handles the saving of the dataset
    if not os.path.exists('dataset.pt'):
        train_dataset,val_dataset,tokenizer = setup_dataset()
        torch.save({'train_dataset':train_dataset,
                    'val_dataset':val_dataset,
                    'tokenizer':tokenizer},'dataset.pt')
    
    # Loads the dataset
    data = torch.load('dataset.pt')
    train_dataset = data['train_dataset']
    val_dataset = data['val_dataset']
    tokenizer = data['tokenizer']

    # Splitting labels for training and testing, setting up data
    print('{:>5,} training docs'.format(len(train_dataset)))
    print('{:>5,} validation docs'.format(len(val_dataset)))

    # Sample in random order when training
    train_dataloader = DataLoader(
                train_dataset,  
                sampler = RandomSampler(train_dataset), 
                batch_size = args.batch_size 
            )

    validation_dataloader = DataLoader(
                val_dataset, 
                sampler = SequentialSampler(val_dataset), 
                batch_size = args.batch_size 
            )

    train(train_dataloader, validation_dataloader,tokenizer,args.epochs,args.validation_epoch,args.output_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser('DETR training and evaluation script', parents=[get_args_parser()])
    args = parser.parse_args()
    if args.output_dir:
        Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    main(args)