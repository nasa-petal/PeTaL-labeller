import json
import logging
import os

import torch
from model import LayerLinearRegression # Import the model that will be used later 


JSON_CONTENT_TYPE = 'application/json'

logger = logging.getLogger(__name__)


def model_fn(model_dir):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info('Current device: {}'.format(device))
    logger.info('Loading the model.')
    
    model = LayerLinearRegression().to(device)
    
    if os.path.exists(os.path.join(model_dir,'model.pth')):
        state_dict = torch.load(os.path.join(model_dir,'model.pth'))
        model.load_state_dict(state_dict)
        
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
        return json.dumps(prediction_output), accept
    raise Exception('Requested unsupported ContentType in Accept: ' + accept)


def predict_fn(input_data, model):
    logger.info('Generating text based on input parameters.')
    m = model['model']
    print(m)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info('Current device: {}'.format(device))

    result = list()
    with torch.no_grad():  # no tracking history
        data = input_data['xvalue']
        print(data)
        data = torch.as_tensor([data],dtype=torch.float32,device=device)
        out = m(data)
        result.append(out)
    result = [str(x) for x in result]
    return ''.join(result)