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
import random 
import pandas as pd
import numpy as np
from transformers import AutoTokenizer
from torch.utils.data import TensorDataset, random_split
from torch.utils.data import DataLoader, RandomSampler, SequentialSampler
from train import train
from nltk.tokenize import word_tokenize

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def get_args_parser():
    def dir_path(path):
        if os.path.isdir(path):
            return path
        else:
            raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


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
    parser.add_argument('--filename', default='golden.csv', type=str)
    parser.add_argument('--epochs_to_train_bert', default=50, type=int)
    parser.add_argument('--batch_size', default=32, type=int)
    parser.add_argument('--num_workers', default=4, type=int)
    parser.add_argument('--epochs_to_classify', default=500, type=int)
    parser.add_argument('--validation_epoch', default=1, type=int, help='At what epoch do we run the validation')
    parser.add_argument('--output_dir',default='epochs',type=str, help='folder where to save checkpoints')
    return parser



def chunks(lst, n):
    """Breaks a large list into chunks 

    Args:
        lst ([type]): large list
        n ([type]): chunks of size n

    Yields:
        list: list of lists with chunk size n
    """
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
        


def setup_dataset(filename:str):
    """Setup the Train and Validation datasets

    Returns:
        (tuple): tuple containing:

            - **train_dataset** (torch.utils.data.TensorDataset): pitch distribution
            - **val_dataset** (torch.utils.data.TensorDataset): pitch to chord distribution
    """
    df = pd.read_csv(filename)
    df = df[df['single_labels'].notnull()]

    single_labels = df["single_labels"].tolist()
    abstracts = df["abstract"].tolist()
    title = df["title"].tolist()
        
    unique_labels = list(set(single_labels))
    single_labels_int = [unique_labels.index(label) for label in single_labels]

    regular_list = [word_tokenize(a) for a in abstracts]
    tokens_flat = [item for sublist in regular_list for item in sublist]
    tokens_flat = set(tokens_flat)
    unique_tokens = (list(tokens_flat))     # convert the set to the list

    tokenizer = AutoTokenizer.from_pretrained("allenai/scibert_scivocab_uncased")
    # Huggingface is crap https://github.com/huggingface/tokenizers/issues/175 
    tokenizer.add_tokens(random.choices(unique_tokens,k=25000))
    # unique_token_chunks = chunks(unique_tokens,50)
    # [tokenizer.add_tokens(chunk) for chunk in unique_token_chunks] # Small lists are fine but extra large lists are tough 

    print('SciBERT tokenizer loaded')

    # original abstract
    print(' Original: ', abstracts[5])
    # abstract split into tokens
    print('Tokenized: ', tokenizer.tokenize(abstracts[5]))
    # abstract as mapped to ids
    print('Token IDs: ', tokenizer.convert_tokens_to_ids(tokenizer.tokenize(abstracts[5])))
   
    # Finishing tokenizing all docs and map tokens to thier word IDs
    input_ids = []
    attention_masks = []
    actual_labels_test = []

    max_abstract_len = max([len(a) for a in abstracts])

    for d in abstracts:
        encoded_dict = tokenizer.encode_plus(
                            d,                      
                            truncation=True,
                            add_special_tokens = True, 
                            max_length = max_abstract_len,           
                            pad_to_max_length = True,
                            return_attention_mask = True,   
                            return_tensors = 'pt',     
                    )
        input_ids.append(encoded_dict['input_ids'])
        attention_masks.append(encoded_dict['attention_mask'])

    # Convert the lists into tensors.
    input_ids = torch.cat(input_ids, dim=0)
    attention_masks = torch.cat(attention_masks, dim=0)
    labels = torch.tensor(single_labels_int)

    print('Original: ', abstracts[5])
    print('Token IDs:', input_ids[5])
    print('Reverse:', tokenizer.convert_ids_to_tokens(input_ids[5]))

    # Split up training & testing/validation
    dataset = TensorDataset(input_ids, attention_masks, labels)

    # Number of docs to include per set
    train_size = int(0.7 * len(dataset))
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
        train_dataset,val_dataset,tokenizer = setup_dataset(args.filename)
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
    parser = argparse.ArgumentParser('Scibert arguments', parents=[get_args_parser()])
    args = parser.parse_args()
    if args.output_dir:
        Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    main(args)