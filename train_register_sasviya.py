import sys
import pandas as pd
from sasviya.ml.tree import ForestClassifier
from sasctl.services import model_repository as mr
from utils import build_X_y, get_or_create_project, get_connection

target = 'Inspection'
nominal_cols = ['CertificateOfOrigin', 'EUCitizen', 
                'Perishable', 'Fragile', 'PreDeclared',
                'MultiplePackage', 'OnlineDeclaration',
                'ExporterValidation', 'SecuredDelivery', 'LithiumBatteries',
                'ExpressDelivery', 'PaperlessBilling', 'Category', 'EntryPoint',
                'Origin', 'PaymentMethod']
project_name = "Workbench Models"
repository_name = "DMRepository"
model_name = "sasviyaModel"

X, y = build_X_y('data/CUSTOMS.csv', target)

sasviya_rf = ForestClassifier()
sasviya_rf.fit(X, y, nominals=nominal_cols)

print("Model trained!")

if len(sys.argv) == 1:
    get_connection()
elif len(sys.argv) == 2:
    verification_file = sys.argv[1]
    print(f"verification_file received: {verification_file}")
    get_connection(verification=verification_file)
elif len(sys.argv) == 3:
    verification_file = sys.argv[1]
    refresh_file = sys.argv[2]
    print(f"verification_file received: {verification_file}")
    print(f"refresh_file received: {refresh_file}")
    get_connection(verification=verification_file, refresh_file=refresh_file)

project = get_or_create_project(project_name, repository_name)

model_params = {
    "name": model_name,
    "projectId": project.id,
    "type": "ASTORE",
}

astore = mr.post(
    "/models",
    files={"files": ("model_export.astore", sasviya_rf.export())},
    data=model_params,
)

print(f"The model '{model_name}' has been registered to SAS Model Manager in the project '{project_name}'!")