import json
import logging
import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np 
import os.path as osp

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
JSON_CONTENT_TYPE = 'application/json'
logger = logging.getLogger(__name__)

def model_fn(model_dir):
    logger.info('Loading the model.')
    model_info = dict()
    model = AutoModelForSequenceClassification.from_pretrained("allenai/scibert_scivocab_uncased", num_labels = 10, output_attentions = False, output_hidden_states = False)
    if os.path.exists(os.path.join(model_dir,'last_saved.pth')):
        state_dict = torch.load(os.path.join(model_dir,'last_saved.pth'))
        model.load_state_dict(state_dict['model'])

    print('model_info: {}'.format(model_info))
    logger.info('Current device: {}'.format(device))
        
    model.to(device).eval()
    logger.info('Model has been loaded')
    return {'model': model}


def input_fn(serialized_input_data, content_type=JSON_CONTENT_TYPE):
    logger.info('Deserializing the input data.')
    if content_type == JSON_CONTENT_TYPE:
        input_data = json.loads(serialized_input_data)
        return input_data
    raise Exception('Requested unsupported ContentType in content_type: ' + content_type)


def output_fn(prediction_output, accept=JSON_CONTENT_TYPE):
    logger.info('Serializing the generated output.')
    if accept == JSON_CONTENT_TYPE:
        return prediction_output
    raise Exception('Requested unsupported ContentType in Accept: ' + accept)


def predict_fn(input_data, model):
    logger.info('Generating text based on input parameters.')
    model = model['model']
    logger.info('Current device: {}'.format(device))

    labels = ["'Protect from harm'", "'Process resources'", "'Sense send or process information'", "'Maintain structural integrity'", "'Move'", "'Attach'", "'Maintain ecological community'", "'Chemically modify or Change energy state'", "'Change size or color'", "'Physically assemble/disassemble'"]

    abstract = input_data['abstract']

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
    results = dict()
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
        # cross_ent = torch.nn.functional.cross_entropy(logits,torch.tensor([actual_label])).detach().cpu().numpy() # Need actual data to compute this

        results = {'abstract':abstract,
                    'predicted_label':labels[pred_index[0]],
                    'confidence': str(preds[0][pred_index[0]]),
                    'hface_Loss': str(float(tmp_eval_loss)),
                    'softmax_loss': np.array2string(softmax_loss), 
                    'log_softmax_loss':np.array2string(log_softmax_loss)
                }

    return json.dumps(results, indent = 4)  