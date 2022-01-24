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
import os, json, sys
from azureml.core import Workspace
from azureml.core import Run
from azureml.core import Experiment
from azureml.core.model import Model

from azureml.core.runconfig import RunConfiguration
from azureml.core.authentication import AzureCliAuthentication
cli_auth = AzureCliAuthentication()

# Get workspace
ws = Workspace.from_config(auth=cli_auth)


# run_id = os.environ["run_id"]
# experiment_name = os.environ["experiment_name"]
#  model_name = os.environ['model_name']
# exp = Experiment(workspace=ws, name=experiment_name)


# try:
#     if not run_id:
#         raise Exception("No new model to register as production model perform better")
# except:
#     print("No new model to register as production model perform better")
#     # raise Exception('No new model to register as production model perform better')
#     sys.exit(0)

# Get the latest evaluation result
try:
    with open("./aml_config/run_id.json") as f:
        config = json.load(f)
    if not config["run_id"]:
        raise Exception("No new model to register as production model perform better")
except:
    print("No new model to register as production model perform better")
    # raise Exception('No new model to register as production model perform better')
    sys.exit(0)

run_id = config["run_id"]
experiment_name = config["experiment_name"]
model_name = config['model_name']



exp = Experiment(workspace=ws, name=experiment_name)

run = Run(experiment=exp, run_id=run_id)
names = run.get_file_names
names()
print("Run ID for last run: {}".format(run_id))
print("Model Name: {}".format(model_name))


model_local_dir = "model"
os.makedirs(model_local_dir, exist_ok=True)

#Register the model via "run" object for CPD
target = 'cpd'
# Download Model to Project root directory
run.download_file(
    name="./outputs/" + model_name.format(target), output_file_path="./model/" + model_name.format(target)
)
print("Downloaded model {} to Project root directory".format(model_name.format(target)))
model_cpd = run.register_model( model_name=model_name.format(target),
                    model_path="./outputs/"+model_name.format(target), # run outputs path
                    description='Regression model for '+ target,
                    tags={'Target': target,'Mode':'Baseload'},
                    model_framework='ScikitLearn',
                    model_framework_version='0.20.3')

#Register the model via "run" object for CTD
target = 'ctd'
# Download Model to Project root directory
run.download_file(
    name="./outputs/" + model_name.format(target), output_file_path="./model/" + model_name.format(target)
)
print("Downloaded model {} to Project root directory".format(model_name.format(target)))
model_ctd = run.register_model( model_name=model_name.format(target),
                    model_path="./outputs/"+model_name.format(target), # run outputs path
                    description='Regression model for '+ target,
                    tags={'Target': target,'Mode':'Baseload'},
                    model_framework='ScikitLearn',
                    model_framework_version='0.20.3')

#Register the model via "run" object for Exh
target = 'Exh'
# Download Model to Project root directory
run.download_file(
    name="./outputs/" + model_name.format(target), output_file_path="./model/" + model_name.format(target)
)
print("Downloaded model {} to Project root directory".format(model_name.format(target)))
model_Exh = run.register_model( model_name=model_name.format(target),
                    model_path="./outputs/"+model_name.format(target), # run outputs path
                    description='Regression model for '+ target,
                    tags={'Target': target,'Mode':'Baseload'},
                    model_framework='ScikitLearn',
                    model_framework_version='0.20.3')

#Register the model via "run" object for MW
target = 'mw'
# Download Model to Project root directory
run.download_file(
    name="./outputs/" + model_name.format(target), output_file_path="./model/" + model_name.format(target)
)
print("Downloaded model {} to Project root directory".format(model_name.format(target)))
model_mw = run.register_model( model_name=model_name.format(target),
                    model_path="./outputs/"+model_name.format(target), # run outputs path
                    description='Regression model for '+ target,
                    tags={'Target': target,'Mode':'Baseload'},
                    model_framework='ScikitLearn',
                    model_framework_version='0.20.3')


#Register the model via "run" object for fuel
target = 'fuel'
# Download Model to Project root directory
run.download_file(
    name="./outputs/" + model_name.format(target), output_file_path="./model/" + model_name.format(target)
)
print("Downloaded model {} to Project root directory".format(model_name.format(target)))
model_fuel = run.register_model( model_name=model_name.format(target),
                    model_path="./outputs/"+model_name.format(target), # run outputs path
                    description='Regression model for '+ target,
                    tags={'Target': target,'Mode':'Baseload'},
                    model_framework='ScikitLearn',
                    model_framework_version='0.20.3')


# #Register the model via "Model" object
# model = Model.register(
#     model_path=model_name,  # this points to a local file
#     model_name=model_name,  # this is the name the model is registered as
#     tags={"target": "CPD", "type": "regression", "run_id": run_id},
#     description="Regression model for predicting cpd",
#     workspace=ws,
# )
# os.chdir("..")
#########Save cpd info to json file#################
print(
    "Model registered: {} \nModel Description: {} \nModel Version: {}".format(
        model_cpd.name, model_cpd.description, model_cpd.version
    )
)

# Writing the registered model details to /aml_config/model_cpd.json
model_json = {}
model_json["model_name"] = model_cpd.name
model_json["model_version"] = model_cpd.version
model_json["run_id"] = run_id
with open("./aml_config/model_cpd.json", "w") as outfile:
    json.dump(model_json, outfile)

#########Save ctd info to json file#################
print(
    "Model registered: {} \nModel Description: {} \nModel Version: {}".format(
        model_ctd.name, model_ctd.description, model_ctd.version
    )
)

# Writing the registered model details to /aml_config/model_ctd.json
model_json = {}
model_json["model_name"] = model_ctd.name
model_json["model_version"] = model_ctd.version
model_json["run_id"] = run_id
with open("./aml_config/model_ctd.json", "w") as outfile:
    json.dump(model_json, outfile)

#########Save Exh info to json file#################
print(
    "Model registered: {} \nModel Description: {} \nModel Version: {}".format(
        model_Exh.name, model_Exh.description, model_Exh.version
    )
)

# Writing the registered model details to /aml_config/model_Exh.json
model_json = {}
model_json["model_name"] = model_Exh.name
model_json["model_version"] = model_Exh.version
model_json["run_id"] = run_id
with open("./aml_config/model_Exh.json", "w") as outfile:
    json.dump(model_json, outfile)


#########Save mw info to json file#################
print(
    "Model registered: {} \nModel Description: {} \nModel Version: {}".format(
        model_mw.name, model_mw.description, model_mw.version
    )
)

# Writing the registered model details to /aml_config/model_mw.json
model_json = {}
model_json["model_name"] = model_mw.name
model_json["model_version"] = model_mw.version
model_json["run_id"] = run_id
with open("./aml_config/model_mw.json", "w") as outfile:
    json.dump(model_json, outfile)

#########Save fuel info to json file#################
print(
    "Model registered: {} \nModel Description: {} \nModel Version: {}".format(
        model_fuel.name, model_fuel.description, model_fuel.version
    )
)

# Writing the registered model details to /aml_config/model_fuel.json
model_json = {}
model_json["model_name"] = model_fuel.name
model_json["model_version"] = model_fuel.version
model_json["run_id"] = run_id
with open("./aml_config/model_fuel.json", "w") as outfile:
    json.dump(model_json, outfile)




