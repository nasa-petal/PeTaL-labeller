'''
    test.py - complements train.py. Performs two functions,
        Function 1: Picks a random abstract and compares it and plots all the errors.
        Function 2: Plots the training loss

   
    Authors: Paht Juangphanich (paht.juangphanich@nasa.gov)
'''
import matplotlib.pyplot as plt
import torch
import pandas as pd 
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os.path as osp
import numpy as np 

def predict_random_sample():
    labels = ["'Protect from harm'", "'Process resources'", "'Sense send or process information'", "'Maintain structural integrity'", "'Move'", "'Attach'", "'Maintain ecological community'", "'Chemically modify or Change energy state'", "'Change size or color'", "'Physically assemble/disassemble'"]

    filename = 'SINGLELABEL_Colleen_and_Alex_training_data_4.19.csv'
    df = pd.read_csv(filename)
    data = df.sample()                                                  # Pick a random sample
    abstract = data['abstract'].values[0]
    actual_label = labels.index(df["single_labels"].values[0])

    tokenizer = AutoTokenizer.from_pretrained("allenai/scibert_scivocab_uncased")
    encoded_dict = tokenizer.encode_plus(
                            abstract,                      
                            truncation=True,
                            add_special_tokens = True, 
                            max_length = 256,           
                            pad_to_max_length = True,
                            return_attention_mask = True,   
                            return_tensors = 'pt',     
                    )
    # Convert to tensor for prediction, batch size is 10
    input_id = torch.tensor(encoded_dict['input_ids'])
    attention_mask = torch.tensor(encoded_dict['attention_mask'])
    labels_tensor = torch.tensor([0])
    # labels_tensor = torch.cat(32*[torch.tensor([actual_label])])

    # Prediction
    model = AutoModelForSequenceClassification.from_pretrained("allenai/scibert_scivocab_uncased", num_labels = 10, output_attentions = False, output_hidden_states = False)
    if osp.exists('epochs/last_saved.pt'):
        state_dict = torch.load('epochs/last_saved.pt')
        model.load_state_dict(state_dict['model'])

    with torch.no_grad():
        outputs = model(input_id, 
                        token_type_ids=None, 
                        attention_mask=attention_mask, 
                        labels=labels_tensor)
        
        tmp_eval_loss, logits = outputs[:2]
        preds = logits.detach().cpu().numpy()
        pred_index = np.argmax(preds, axis=1)
    
        softmax_loss = torch.nn.functional.softmax(logits).detach().cpu().numpy()
        log_softmax_loss = torch.nn.functional.log_softmax(logits).detach().cpu().numpy()
        cross_ent = torch.nn.functional.cross_entropy(logits,torch.tensor([actual_label])).detach().cpu().numpy()

        print('\n\nAbstract: '+ abstract)
        print("Actual Label: " + labels[actual_label])
        print('Predicted Label: ' + labels[pred_index[0]])
        print('Prediction confidence: ' + str(preds[0][pred_index[0]]))

        print(f'HFace Bert Loss: {float(tmp_eval_loss)}')
        print(f'Softmax Losses: {softmax_loss}')
        print(f'Log Softmax Loss: {log_softmax_loss}')
        print(f'Cross Entropy Loss: {cross_ent}')

def plot_training():
    last = torch.load('epochs/last_saved.pt')
    df = pd.DataFrame(last['training_stats'])
    plt.figure(figsize=(8,6),dpi=150)
    fig, ax = plt.subplots(1,2)
    ax[0].plot(df['epoch'],df['Training Loss'])    
    ax[0].set_xlabel('Epoch')
    ax[0].set_ylabel('Avg Cross Entropy Loss')   
    ax[0].set_yscale('log')
    ax[0].set_title('Training Loss vs Epoch')

    ax[1].plot(df['epoch'][1:],df['Valid. Accur.'][1:])    
    ax[1].set_xlabel('Epoch')
    ax[1].set_ylabel('Avg Cross Entropy Loss')
    ax[1].set_yscale('log')
    ax[1].set_title('Validation Loss vs Epoch')
    plt.savefig('training_loss.png')
    

if __name__ == '__main__':
    plot_training()
    predict_random_sample()