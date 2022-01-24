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
from azureml.core import Experiment
from azureml.core import Environment
from azureml.core.compute import RemoteCompute
from azureml.core.runconfig import RunConfiguration
from azureml.core import ScriptRunConfig
import azureml.core
from azureml.core.authentication import AzureCliAuthentication

#Set up parameters for passing the model metadata
import argparse
# Set script arguments
parser = argparse.ArgumentParser()
parser.add_argument('--dataset', type=str  , dest='dataset_name', default='DB_GT3_Baseload',help='dataset name')
# parser.add_argument('--training_target', type=str  , dest='target_name', default='',help='training target column name')
# parser.add_argument('--training_input', nargs="+", dest='input_name', default=[],help='training input columns name in a list')


args = parser.parse_args()
dataset_name = args.dataset_name#'DB_GT3_Baseload_cpd'#
# training_target = args.target_name
# training_columns =args.input_name #['Baseload_cit_clean', 'Baseload_baro_clean']

# print('=========================================')
# print('Input Parameters for TrainOnCluster:',args)
# print(' '.join(args.input_name))

cli_auth = AzureCliAuthentication()
# Get workspace
ws = Workspace.from_config(auth=cli_auth)


# Read the New VM Config
with open("./aml_config/security_config.json") as f:
    config = json.load(f)
aml_cluster_name = config["aml_cluster_name"]


# Attach Experiment
experiment_name = "cct_aml"
exp = Experiment(workspace=ws, name=experiment_name)
print(exp.name, exp.workspace.name, sep="\n")

# run_config = RunConfiguration()
# run_config.target = aml_cluster_name

# Set up running enviroment from conda YAML file
env = Environment.from_conda_specification(
    name='training_environment',
    file_path='./aml_config/conda_dependencies_cct.yml',
)

script_config = ScriptRunConfig(source_directory="./code/training",
                                script='train_multi_models.py',
                                arguments =
                                 ['--dataset', dataset_name],
                                #   '--training_target',training_target,
                                #   '--training_input',' '.join(training_columns)],                                            
                                environment=env,
                                compute_target = aml_cluster_name) 


run = exp.submit(script_config)

# Shows output of the run on stdout.
run.wait_for_completion(show_output=True, wait_post_processing=True)

# Raise exception if run fails
if run.get_status() == "Failed":
    raise Exception(
        "Training on cluster failed with following run status: {} and logs: \n {}".format(
            run.get_status(), run.get_details_with_logs()
        )
    )

# Writing the run id to /aml_config/run_id.json
run_id = {}
run_id["run_id"] = run.id
run_id["experiment_name"] = run.experiment.name
run_id["model_name"] = 'DB_GT3_Baseload_model_{}.pkl'
with open("./aml_config/run_id.json", "w") as outfile:
    json.dump(run_id, outfile)

print('From Training Script, run id:',run.id)

# print('current dir:',os.getcwd())

# #Set pipeline variable "run_id" for later tasks use
# print('echo \"##vso[task.setvariable variable=run_id;]%s\"' % run_id["run_id"])
# print('echo \"##vso[task.setvariable variable=experiment_name;]%s\"' % run_id["experiment_name"])
# print('echo \"##vso[task.setvariable variable=model_name;]%s\"' % run_id["model_name"])

# print('All variables:',os.environ)

# print('SystemVariables',sys.argv[1])