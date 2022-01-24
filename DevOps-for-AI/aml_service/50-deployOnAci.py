"""
Copyright (C) Microsoft Corporation. All rights reserved.​
 ​
Microsoft Corporation (“Microsoft”) grants you a nonexclusive, perpetual,
royalty-free right to use, copy, and modify the software code provided by us
("Software Code"). You may not sublicense the Software Code or any use of it
(except to your affiliates and to vendors to perform work on your behalf)
through distribution, network access, service agreement, lease, rental, or
otherwise. This license does not purport to express any claim of ownership over
data you may have shared with Microsoft in the creation of the Software Code.
Unless applicable law gives you more rights, Microsoft reserves all other
rights not expressly granted herein, whether by implication, estoppel or
otherwise. ​
 ​
THE SOFTWARE CODE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
MICROSOFT OR ITS LICENSORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THE SOFTWARE CODE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""
import os, json, datetime, sys
from operator import attrgetter
from azureml.core import Workspace
from azureml.core.model import Model
from azureml.core.image import Image
from azureml.core.webservice import Webservice
from azureml.core.webservice import AciWebservice
from azureml.core.authentication import AzureCliAuthentication
from azureml.core.model import InferenceConfig
from azureml.core.model import Model
from azureml.core.webservice import AciWebservice

cli_auth = AzureCliAuthentication()
# Get workspace
ws = Workspace.from_config(auth=cli_auth)# Get the Image to deploy details


#Set up Azure container instance (ACI) configuration
aci_config = AciWebservice.deploy_configuration(cpu_cores=0.1, memory_gb=0.5)

#Define deployment function
def deploy_model(target,aci_config,ws):
    try:
        with open("aml_config/model_{}.json".format(target)) as f:
            model_config = json.load(f)
    except:
        print("No new model, thus no deployment on ACI")
        # raise Exception('No new model to register as production model perform better')
        sys.exit(0)
    #Define inference config
    inference_config = InferenceConfig(runtime= "python",
                                            source_directory = 'code/scoring',
                                            entry_script="EntryScript_{}.py".format(target),
                                            conda_file="conda_dependencies_cct.yml")
    # Deploy the model to ACI instance
    modelName = model_config["model_name"]
    modelVersion = model_config["model_version"]
    model = Model(ws, modelName, version=modelVersion)
    service = Model.deploy(workspace=ws,
                        name = '{}-aci'.format('bd-gt3-baseload-{}'.format(target)).lower(),
                        models = [model],
                        inference_config = inference_config,
                        deployment_config = aci_config,
                        overwrite=True)
                        #deployment_target = production_cluster)
    service.wait_for_deployment(show_output = True)
    return {'ModelName': service.name,'url': service.scoring_uri}


######################Deploy CPD model###################################
target = 'cpd'
cpd_entpoint = deploy_model(target,aci_config,ws)
######################Deploy CTD model###################################
target = 'ctd'
ctd_entpoint = deploy_model(target,aci_config,ws)
######################Deploy Exh model###################################
target = 'Exh'
Exh_entpoint = deploy_model(target,aci_config,ws)
######################Deploy MW model###################################
target = 'mw'
mw_entpoint = deploy_model(target,aci_config,ws)
# ######################Deploy fuel model###################################
target = 'fuel'
fuel_entpoint = deploy_model(target,aci_config,ws)

# Writing the ACI details to /aml_config/aci_webservice.json
aci_webservice = {}
aci_webservice["cpd"] = cpd_entpoint
aci_webservice["ctd"] = ctd_entpoint
aci_webservice["Exh"] = Exh_entpoint
aci_webservice["mw"] = mw_entpoint
aci_webservice["fuel"] = fuel_entpoint


with open("aml_config/aci_webservice.json", "w") as outfile:
    json.dump(aci_webservice, outfile)

##############Update the model end point to digital twin################
from azure.digitaltwins.core import DigitalTwinsClient
from azure.identity import ClientSecretCredential
adt_url = 'CCTwinADT.api.scus.digitaltwins.azure.net'
client_id = '018df2ec-9538-4980-9ed8-f97b81772c73'
tenant_id = '59d6a186-f64d-4298-bcf3-59c83649e16c'
client_secret = '-4MKn5-~FhTmKx4QIDZv8-1Ro4.0t1M.2e'
credential = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id,
                                    client_secret=client_secret)
service_client = DigitalTwinsClient(adt_url, credential)

model_id = "dtmi:cctwin:company:power_block:ml_model;1"
properties = {"model_url_key":
    {'base<cpd><baro|cit>': cpd_entpoint['url'],
     'base<ctd><baro|cit>': ctd_entpoint['url'],
     'base<exh_temp><baro|cpd>': Exh_entpoint['url'],
     'base<mw><baro|cit|cpd|ctd|exh_temp>':  mw_entpoint['url'],
     'base<fuel><mw>': fuel_entpoint['url']
     }}
twin = {'$metadata':{'$model': model_id }}
twin.update(properties)
service_client.upsert_digital_twin(digital_twin_id='bdec_gt3_models', digital_twin=twin)


