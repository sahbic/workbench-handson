import sys
import pandas as pd
from sasviya.ml.tree import ForestClassifier
from sasctl.services import model_repository as mr
from establish_connection import get_connection

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

df = pd.read_csv('data/CUSTOMS.csv')
X = df.drop([target, "packageID"], axis=1)
y = df[target]

sasviya_rf = ForestClassifier()
sasviya_rf.fit(X, y, nominals=nominal_cols)

print("Model trained!")

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

repository = mr.get_repository(repository_name)

try:
    project = mr.create_project(project_name, repository)
except:
    project = mr.get_project(project_name)

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