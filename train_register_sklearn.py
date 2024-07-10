import sys
import pickle
import warnings

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder, OneHotEncoder

from sasctl import pzmm
from sasctl.services import model_repository as mr

from establish_connection import get_connection

warnings.filterwarnings("ignore", message="The following arguments are required for the automatic generation of score code")
warnings.filterwarnings("ignore", message="This model's properties are different from the project's.")

storage_name = "myfolder_new"
script_folder = "workbench-handson/"

target = 'Inspection'
binary_cols = ['CertificateOfOrigin', 'Perishable', 'Fragile',
               'PreDeclared', 'PaperlessBilling']
ohe_cols = ['MultiplePackage', 'OnlineDeclaration',
            'ExporterValidation', 'SecuredDelivery', 'LithiumBatteries',
            'ExpressDelivery', 'Category', 'EntryPoint', 'Origin', 'PaymentMethod']
binary_mapping = [['No', 'Yes']]
pklFileName = f'/workspaces/{storage_name}/{script_folder}sklearn_mm_assets/sklearnPipeline.pkl'
project_name = "Workbench Models"
repository_name = "DMRepository"

df = pd.read_csv('data/CUSTOMS.csv')
X = df.drop([target, "packageID"], axis=1)
y = df[target]

# Define the preprocessing steps
preprocessor = ColumnTransformer(
    transformers=[
        ('binary', OrdinalEncoder(categories=[['No', 'Yes']]*len(binary_cols)), binary_cols),
        ('ohe', OneHotEncoder(dtype='int64', handle_unknown='ignore', sparse_output=False), ohe_cols),
        ('impute', SimpleImputer(), ['Price'])
    ],
    remainder='passthrough',  # Keep the remaining columns as they are
    force_int_remainder_cols=False
)

# Define the pipeline
pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(random_state=0))
])

pipeline.fit(X, y)

print('Pipeline trained!')

with open(pklFileName, 'wb') as file:
    pickle.dump(pipeline, file)

if len(sys.argv) == 1:
    get_connection()
elif len(sys.argv) == 2:
    refresh_file = sys.argv[1]
    get_connection(refresh_file=refresh_file)
elif len(sys.argv) == 3:
    refresh_file = sys.argv[1]
    verification_file = sys.argv[2]
    print(f"refresh_file received: {refresh_file}")
    print(f"verification_file received: {verification_file}")
    get_connection(verification=verification_file, refresh_file=refresh_file)

target_df =pd.DataFrame(data=[[0.8,0.2,"No"]],columns=['P_InspectionNo','P_InspectionYes','I_Inspection'])

pzmm.JSONFiles.write_var_json(X, is_input=True, json_path=f"/workspaces/{storage_name}/{script_folder}sklearn_mm_assets/")
pzmm.JSONFiles.write_var_json(target_df, is_input=False, json_path=f"/workspaces/{storage_name}/{script_folder}sklearn_mm_assets/")

model_name = "sklearnPipeline"

pzmm.JSONFiles.write_model_properties_json(model_name=model_name,
                            model_desc='scikit-learn Random Forest Classification model',
                            target_variable='Inspection',
                            model_algorithm='sklearn.ensemble.RandomForestClassifier',
                            target_values=["No","Yes"],
                            json_path=f"/workspaces/{storage_name}/{script_folder}sklearn_mm_assets/",
                            modeler='Mattia')

repository = mr.get_repository(repository_name)

try:
    project = mr.create_project(project_name, repository)
except:
    project = mr.get_project(project_name)

import_model = pzmm.ImportModel.import_model(
    overwrite_model=True,
    model_files=f"/workspaces/{storage_name}/{script_folder}sklearn_mm_assets/",
    model_prefix=model_name,
    project=project_name
)

print(f"The model '{model_name}' has been registered to SAS Model Manager in the project '{project_name}'!")

model = mr.get_model(model_name)

scorefile = mr.add_model_content(
    model,
    open(f'/workspaces/{storage_name}/{script_folder}sklearn_mm_assets/sklearnPipelineScore.py', 'rb'),
    name='sklearnPipelineScore.py',
    role='score'
)

print("The scoring code has been added to the model!")

python_pickle = mr.add_model_content(
    model,
    open(pklFileName, 'rb'),
    name=pklFileName,
    role='python pickle'
)

print("The pickle file has been added to the model!")