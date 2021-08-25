import base64
import pickle
import requests

def save_ML_model(model_object, model_name, workspace, project, token):    
    
    """
    Saves a ML model into a given Quix repository.
    
    model_object: python ml model object already trained.
    model_name: name for our model to be saved with in the repository.
    worskpace: Quix workspace id
    project: Quix code project name
    token: Quix token
    """
    
    url = "https://portal-api.platform.quix.ai/{}/projects/{}/files/source%2FMLModels%2F{}.pickle?branch=master".format(workspace, project, model_name)
    
    head = {'Authorization': 'Bearer {}'.format(token), 
            'Content-Type': 'text/plain'}
    
    # Convert dictionary data to binary and then text
    model_base64_str = base64.b64encode(pickle.dumps(model_object, protocol=pickle.HIGHEST_PROTOCOL))
    
    response = requests.post(url, headers=head, data=model_base64_str)
    print(response)