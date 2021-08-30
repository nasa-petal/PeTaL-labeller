'''
    train.py - performs the training and saving of the model at each epoch. 

    Authors: Paht Juangphanich (paht.juangphanich@nasa.gov)
'''
import os
import torch
from torch.nn import utils
from torch.utils.data import DataLoader
from torch.utils.data.dataset import Dataset
from transformers import get_linear_schedule_with_warmup
from transformers import AdamW
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import TrainingArguments
from transformers import Trainer
from torch.utils.data import DataLoader, RandomSampler, SequentialSampler

import numpy as np
from tqdm import tqdm

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Calculate accuracy of predictions vs labels
def flat_accuracy(preds, labels):
    """Outputs a flattened accuracy score 

    Args:
        preds ([type]): [description]
        labels ([type]): [description]

    Returns:
        [type]: [description]
    """
    pred_flat = np.argmax(preds, axis=1).flatten()
    labels_flat = labels.flatten()
    return np.sum(pred_flat == labels_flat) / len(labels_flat)

def print_model(model):
    """Prints Bert Model

    Args:
        model ([type]): [description]
    """
    params = list(model.named_parameters())
    print('model has {:} different named parameters\n'.format(len(params)))
    print('Embedding Layer: \n')

    for p in params[0:5]:
        print("{:<55} {:>12}".format(p[0], str(tuple(p[1].size()))))

    print('\nFirst Transformer:\n')
    for p in params[5:21]:
        print("{:<55} {:>12}".format(p[0], str(tuple(p[1].size()))))

    print('\nOutput Layer:\n')
    for p in params[-4:]:
        print("{:<55} {:>12}".format(p[0], str(tuple(p[1].size()))))

def train_one_epoch(model,train_loader:DataLoader,optimizer:AdamW,scheduler:torch.optim.lr_scheduler.LambdaLR,epoch:int,max_epoch:int):
    """Loops through the dataloader and trains the model and optimizer

    Args:
        model ([BertForSequenceClassification]): [description]
        dataloader (DataLoader): [description]
        optimizer (AdamW): [description]
        scheduler (torch.optim.lr_scheduler.LambdaLR): [description]

    Returns:
        [type]: [description]
    """

    total_loss = 0
    model.train()
    train_bar = tqdm(train_loader)
    train_bar.desc = f"Epoch {epoch}/{max_epoch} Loss: 0"
    for batch in train_bar:
        # `batch` pytorch tensors:
        #   [0]: input ids 
        #   [1]: attention masks
        #   [2]: labels 
        b_input_ids = batch[0].to(device)
        b_input_mask = batch[1].to(device)
        b_labels = batch[2].to(device)

        model.zero_grad()        

        outputs = model(b_input_ids, 
                    token_type_ids=None, 
                    attention_mask=b_input_mask, 
                    labels=b_labels)
        
        tmp_eval_loss, logits = outputs[:2]
        loss = tmp_eval_loss # torch.nn.functional.cross_entropy(logits,b_labels)

        total_loss += loss.item()
        loss.backward()
        utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()    
        train_bar.desc = f"Epoch {epoch}/{max_epoch} Batch Loss: {loss.item()}" # Note cross entropy loss does not increase with batch size

    avg_train_loss = total_loss / len(train_loader)            
    return model, optimizer, scheduler, avg_train_loss


@torch.no_grad()
def validation(validation_loader,model):
    """Computes the validation accuracy

    Args:
        validation_loader ([type]): [description]
        model ([type]): [description]

    Returns:
        [type]: [description]
    """
    eval_accuracy = 0 
    nb_eval_steps = 0 

    for batch in validation_loader:            
        batch = tuple(t.to(device) for t in batch)
        b_input_ids, b_input_mask, b_labels = batch
        outputs = model(b_input_ids, 
                        token_type_ids=None, 
                        attention_mask=b_input_mask)
        
        logits = outputs[0]
        logits = logits.detach().cpu().numpy()
        label_ids = b_labels.to('cpu').numpy()
        
        tmp_eval_accuracy = flat_accuracy(logits, label_ids)
        
        eval_accuracy += tmp_eval_accuracy
        nb_eval_steps += 1
    val_error = eval_accuracy/nb_eval_steps

    return val_error

def train(train_dataset:Dataset,val_dataset:Dataset,tokenizer:AutoTokenizer,epochs:int,val_epochs:int,save_folder:str,epochs_bert:int,number_of_labels:int=10,batch_size:int=16):
    """Trains the model for a given nubmer of epochs. Runs validation every val_epochs

    Args:
        train_dataloader (Dataset): train dataset
        val_dataloader (Dataset): validation dataset
        tokenizer (AutoTokenizer): word tokenizer
        epochs (int): number of epochs to run 
        val_epochs (int): at what epoch should validation be performed 
        save_folder (str): where to save the file
        epochs_bert (int): additional number of epochs to train bert with new tokens
        number_of_labels(int): number of labels to predict 
    """
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
    # Possible hyperparamters: 
    # * batch size: 16, 32
    # * learning rate: 5e-5, 3e-5, 2e-5
    # * number of epochs: 2, 3, 4

    model = AutoModelForSequenceClassification.from_pretrained("allenai/scibert_scivocab_uncased", num_labels = number_of_labels, output_attentions = False, output_hidden_states = False)
    model.resize_token_embeddings(len(tokenizer))
    
    # Train bert for a few epochs before actually classifying 
    if epochs_bert>0:
        training_args = TrainingArguments(evaluation_strategy="epoch",num_train_epochs=epochs_bert)
        trainer = Trainer(model=model, args=training_args,      train_dataset=train_dataloader.data, eval_dataset=val_dataloader.data)
        trainer.train()

    # Train the rest
    optimizer = AdamW(model.parameters(), lr = 5e-5, eps = 1e-8)

    # this needs to be run on GPU
    model.to(device)
    # Training epochs should be betw 2- 4 (reduce if overfitting)
    total_steps = len(train_dataloader) * epochs    
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps = 0, num_training_steps = total_steps) # LR scheduler
    
    # Check to see if training has been performed, reload last if exists
    val_losses = 0
    training_stats = list()
    last_saved = os.path.join(save_folder,'last_saved.pt')
    if (os.path.exists(last_saved)):
        data = torch.load(last_saved)
        model.load_state_dict(data['model'])
        optimizer.load_state_dict(data['optimizer'])
        training_stats.extend(data['training_stats'])
        start_epoch = training_stats[-1]['epoch']
    else:
        start_epoch = 0
    # based on the `run_glue.py` script here:
    # https://github.com/huggingface/transformers/blob/5bfcd0485ece086ebcbed2d008813037968a9e58/examples/run_glue.py#L128
    train_losses = list()
    val_losses = list()
    
    
    for epoch in range(start_epoch+1,epochs):
        model, optimizer, scheduler, avg_train_loss = train_one_epoch(model,train_dataloader,optimizer,scheduler,epoch,epochs)

        train_losses.append(avg_train_loss)
        val_losses = validation(val_dataloader, model)
        
        training_stats.append(
            {
                'epoch': epoch + 1,
                'Training Loss': avg_train_loss,
                'Valid. Accur.': val_losses
            }
        )
        
        torch.save({'model':model.state_dict(),'optimizer':optimizer.state_dict(),'training_stats':training_stats}, os.path.join(save_folder,f'epoch_{epoch}.pt'))
        torch.save({'model':model.state_dict(),'optimizer':optimizer.state_dict(),'training_stats':training_stats}, last_saved)

    return model, optimizer, scheduler, training_stats