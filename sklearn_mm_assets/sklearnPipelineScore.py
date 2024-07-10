import settings
import pickle
import pandas as pd

with open(settings.pickle_path+'/sklearnPipeline.pkl', "rb") as f:
    pipeline = pickle.load(f)

def score_method(CertificateOfOrigin, EUCitizen, Perishable, Fragile, Volume,
                 PreDeclared, MultiplePackage, Category, OnlineDeclaration,
                 ExporterValidation, SecuredDelivery, LithiumBatteries,
                 ExpressDelivery, EntryPoint, Origin, PaperlessBilling,
                 PaymentMethod, Weight, Price):
    "Output: P_InspectionNo, P_InspectionYes, I_Inspection"

    df = pd.DataFrame([[CertificateOfOrigin, EUCitizen, Perishable, Fragile, Volume,
                            PreDeclared, MultiplePackage, Category, OnlineDeclaration,
                            ExporterValidation, SecuredDelivery, LithiumBatteries,
                            ExpressDelivery, EntryPoint, Origin, PaperlessBilling,
                            PaymentMethod, Weight, Price]],
                            columns=['CertificateOfOrigin', 'EUCitizen', 'Perishable', 'Fragile', 'Volume',
                                    'PreDeclared', 'MultiplePackage', 'Category', 'OnlineDeclaration',
                                    'ExporterValidation', 'SecuredDelivery', 'LithiumBatteries',
                                    'ExpressDelivery', 'EntryPoint', 'Origin', 'PaperlessBilling',
                                    'PaymentMethod', 'Weight', 'Price'])
    
    y_pred_prob = pipeline.predict_proba(df)
    y_pred = pipeline.predict(df)
       
    return float(y_pred_prob[0][0]), float(y_pred_prob[0][1]), str(y_pred[0])