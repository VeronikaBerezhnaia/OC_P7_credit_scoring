import pandas as pd
import streamlit as st
import requests

import matplotlib.pyplot as plt
import numpy as np
import shap
import joblib
import sklearn # if is needed for using columntransformer methods

def request_prediction(model_uri, columns, data):
    headers = {"Content-Type": "application/json"}

    data_json = {'columns': columns, 'data': data}
    response = requests.request(
        method='POST', headers=headers, url=model_uri, json=data_json)

    if response.status_code != 200:
        raise Exception(
            "Request failed with status {}, {}".format(response.status_code, response.text))

    return response.json()


def main():
    MLFLOW_URI = 'http://127.0.0.1:5000/invocations'
#    CORTEX_URI = 'http://0.0.0.0:8890/'
#    RAY_SERVE_URI = 'http://127.0.0.1:8000/regressor'

#    api_choice = st.sidebar.selectbox('Quelle API souhaitez vous utiliser', ['MLflow', 'Cortex', 'Ray Serve'])

#    st.title('Credit default prediction')
#    NAME_INCOME_TYPE = st.text_input('Just enter Working for the moment')

    NAME_INCOME_TYPE = st.selectbox('Select income type',
        ('Working', 'State servant', 'Commercial associate', 'Pensioner', 'Unemployed', 'Student', 'Businessman', 'Maternity leave'))
#    st.write('You selected:', option)
    AMT_ANNUITY = st.number_input('Loan annuity	natural logarithm: enter any positive float number',
                                   min_value=0., max_value=100., value=12., step=1.)
    AMT_CREDIT = st.number_input('Credit amount of the loan	natural logarithm: enter any positive float number',
                                   min_value=0., max_value=100., value=12., step=1.)
    EXT_SOURCE_1 = st.number_input('Normalized score from external data source 1: enter any float number between 0 and 1',
                                   min_value=0., max_value=1., value=0., step=1.)
    EXT_SOURCE_2 = st.number_input('Normalized score from external data source 2: enter any float number between 0 and 1',
                                   min_value=0., max_value=1., value=0., step=1.)
    EXT_SOURCE_3 = st.number_input('Normalized score from external data source 3: enter any float number between 0 and 1',
                                   min_value=0., max_value=1., value=0., step=1.)
    DAYS_BIRTH = st.number_input('Client age in days at the time of application: enter any positive integer number',
                                   min_value=0., max_value=50000., value=16500., step=1.)
    DAYS_EMPLOYED = st.number_input('How many days before the application the person started current employment: enter any positive float number',
                                   min_value=0., max_value=50000., value=0., step=1.)
    status_unique = ['0', '1', '2', '3', '4', '5', 'C', 'X']
#    STATUS_UNIQUE = ['0', '1', '2', '3', '4', '5', 'C', 'X']
    STATUS = st.selectbox('Status of Credit Bureau loan during the month: active, closed, DPD0-30. C means closed, X means status unknown, 0 means no DPD, 1 means maximal did during month between 1-30, 2 means DPD 31-60... 5 means DPD 120+ or sold or written off )', status_unique, index=7)
    credit_active_unique = ['Active', 'Bad_debt', 'Closed', 'Sold']
    CREDIT_ACTIVE = st.selectbox('Status of the Credit Bureau (CB) reported credits', ['No reported credits', *credit_active_unique]) # if there were no credits before or another issue
    credit_type_unique = ["Another_type_of_loan", "Cash_loan_(non-earmarked)", "Consumer_credit", "Credit_card", "Microloan", "Unknown_type_of_loan",]
    CREDIT_TYPE = st.selectbox('Type of Credit Bureau credit (Car, cash,...) For no reported credits select unknown type of loan', credit_type_unique) # eventually I can fill all the columns with 0 when no reported credits. then I do as with CREDIT_ACTIVE
    FLAG_EMP_PHONE = st.number_input('Did client provide work phone (1=YES, 0=NO): enter 0 or 1',
                              min_value=0., max_value=1., value=0., step=1.)
    FLAG_WORK_PHONE = st.number_input('Did client provide home phone (1=YES, 0=NO): enter 0 or 1',
                              min_value=0., max_value=1., value=0., step=1.)
    FLAG_PHONE = st.number_input('Did client provide home phone (again) (1=YES, 0=NO): enter 0 or 1',
                              min_value=0., max_value=1., value=0., step=1.)
    REGION_RATING_CLIENT_W_CITY = st.number_input('Our rating of the region where client lives with taking city into account (1,2,3)',
                              min_value=0., max_value=1., value=0., step=1.)
    REG_CITY = st.text_input('Registration city', 'Paris')
    LIVE_CITY = st.text_input('Live city', 'Paris')
    WORK_CITY = st.text_input('Work city', 'Paris')
    FLAG_DOCUMENT_2 = st.number_input('Did client provide document 2: enter 0 or 1', #
                              min_value=0., max_value=1., value=0., step=1.)
    FLAG_DOCUMENT_3 = st.number_input('Did client provide document 3: enter 0 or 1', #
                              min_value=0., max_value=1., value=0., step=1.)
    FLAG_DOCUMENT_6 = st.number_input('Did client provide document 6: enter 0 or 1', #
                              min_value=0., max_value=1., value=0., step=1.)
    FLAG_DOCUMENT_9 = st.number_input('Did client provide document 9: enter 0 or 1', #
                              min_value=0., max_value=1., value=0., step=1.)
    FLAG_DOCUMENT_13 = st.number_input('Did client provide document 13: enter 0 or 1', #
                              min_value=0., max_value=1., value=0., step=1.)
    FLAG_DOCUMENT_14 = st.number_input('Did client provide document 14: enter 0 or 1', #
                              min_value=0., max_value=1., value=0., step=1.)
    FLAG_DOCUMENT_16 = st.number_input('Did client provide document 16: enter 0 or 1', #
                              min_value=0., max_value=1., value=0., step=1.)
    FLAG_DOCUMENT_21 = st.number_input('Did client provide document 21: enter 0 or 1', #
                              min_value=0., max_value=1., value=0., step=1.)
    CNT_CHILDREN = st.number_input('Number of children the client has', 
                              min_value=0., value=0., step=1.)
    CNT_FAM_MEMBERS = st.number_input('How many family members does client have', 
                              min_value=1., value=1., step=1.)
    CODE_GENDER = st.text_input('Gender of the client: please enter M for masculin or F for feminin', 'M')


    columns = ["NAME_INCOME_TYPE", "AMT_ANNUITY", "EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3", "DAYS_EMPLOYED_PERC", "CREDIT_TERM", 
    "STATUS_0_SUM", "STATUS_1_SUM", "STATUS_2_SUM", "STATUS_3_SUM", "STATUS_4_SUM", "STATUS_5_SUM", "STATUS_C_SUM", "STATUS_X_SUM", 
    "CREDIT_ACTIVE_Active_SUM", "CREDIT_ACTIVE_Bad_debt_SUM", "CREDIT_ACTIVE_Closed_SUM", "CREDIT_ACTIVE_Sold_SUM", "CREDIT_TYPE_Another_type_of_loan_SUM", "CREDIT_TYPE_Cash_loan_(non-earmarked)_SUM", "CREDIT_TYPE_Consumer_credit_SUM", "CREDIT_TYPE_Credit_card_SUM", "CREDIT_TYPE_Microloan_SUM", "CREDIT_TYPE_Unknown_type_of_loan_SUM", 
    "DAYS_BIRTH", "FLAG_EMP_PHONE", "FLAG_WORK_PHONE", "FLAG_PHONE", "REGION_RATING_CLIENT_W_CITY", "REG_CITY_NOT_LIVE_CITY", "REG_CITY_NOT_WORK_CITY", "LIVE_CITY_NOT_WORK_CITY", "FLAG_DOCUMENT_2", "FLAG_DOCUMENT_3", "FLAG_DOCUMENT_6", "FLAG_DOCUMENT_9", 
    "FLAG_DOCUMENT_13", "FLAG_DOCUMENT_14", "FLAG_DOCUMENT_16", "FLAG_DOCUMENT_21", "F_AGE", "M_AGE", "CNT_ADULTS"]
    
    data = [[NAME_INCOME_TYPE, AMT_ANNUITY, EXT_SOURCE_1, EXT_SOURCE_2, EXT_SOURCE_3, DAYS_EMPLOYED/DAYS_BIRTH, AMT_CREDIT/AMT_ANNUITY, *[int(i == STATUS) for i in status_unique], *[int(i==CREDIT_ACTIVE) for i in credit_active_unique], *[int(i==CREDIT_TYPE) for i in credit_type_unique], 
    DAYS_BIRTH, FLAG_EMP_PHONE, FLAG_WORK_PHONE, FLAG_PHONE, REGION_RATING_CLIENT_W_CITY, int(REG_CITY != LIVE_CITY), int(REG_CITY != WORK_CITY), int(LIVE_CITY != WORK_CITY), FLAG_DOCUMENT_2, FLAG_DOCUMENT_3, FLAG_DOCUMENT_6, FLAG_DOCUMENT_9, FLAG_DOCUMENT_13, FLAG_DOCUMENT_14, 
    FLAG_DOCUMENT_16, FLAG_DOCUMENT_21, DAYS_BIRTH if CODE_GENDER == 'F' else 0, DAYS_BIRTH if CODE_GENDER == 'M' else 0, CNT_FAM_MEMBERS - CNT_CHILDREN]]
    
    data_for_shap = pd.DataFrame(data, columns=columns)
        
    predict_btn = st.button('Predict')
    if predict_btn:

        pred = None

  #      if api_choice == 'MLflow':
        pred = request_prediction(MLFLOW_URI, columns, data)[0]
 #       elif api_choice == 'Cortex':
 #           pred = request_prediction(CORTEX_URI, columns, data)[0]
  #      elif api_choice == 'Ray Serve':
   #         pred = request_prediction(RAY_SERVE_URI, columns, data)[0]
        st.write(
            'The predicted flag of the credit default is {:.1f}'.format(pred))
            
    # draw the graphics (age sex distribution, with the age of client indicated on it)
    # CAUTION: I took the target0 curve and the target1 curve as they were drawn in seaborn kdeplot (see the notebook)
    male_ok_x = np.array([17.55566165, 17.83150478, 18.10734791, 18.38319105, 18.65903418, 18.93487731, 19.21072045, 19.48656358, 19.76240671, 20.03824985, 20.31409298, 20.58993611, 20.86577924, 21.14162238, 21.41746551, 21.69330864, 21.96915178, 22.24499491, 22.52083804, 22.79668118, 23.07252431, 23.34836744, 23.62421057, 23.90005371, 24.17589684, 24.45173997, 24.72758311, 25.00342624, 25.27926937, 25.55511251, 25.83095564, 26.10679877, 26.38264191, 26.65848504, 26.93432817, 27.2101713, 27.48601444, 27.76185757, 28.0377007, 28.31354384, 28.58938697, 28.8652301, 29.14107324, 29.41691637, 29.6927595, 29.96860264, 30.24444577, 30.5202889, 30.79613203, 31.07197517, 31.3478183, 31.62366143, 31.89950457, 32.1753477, 32.45119083, 32.72703397, 33.0028771, 33.27872023, 33.55456337, 33.8304065, 34.10624963, 34.38209276, 34.6579359, 34.93377903, 35.20962216, 35.4854653, 35.76130843, 36.03715156, 36.3129947, 36.58883783, 36.86468096, 37.1405241, 37.41636723, 37.69221036, 37.96805349, 38.24389663, 38.51973976, 38.79558289, 39.07142603, 39.34726916, 39.62311229, 39.89895543, 40.17479856, 40.45064169, 40.72648483, 41.00232796, 41.27817109, 41.55401422, 41.82985736, 42.10570049, 42.38154362, 42.65738676, 42.93322989, 43.20907302, 43.48491616, 43.76075929, 44.03660242, 44.31244556, 44.58828869, 44.86413182, 45.13997495, 45.41581809, 45.69166122, 45.96750435, 46.24334749, 46.51919062, 46.79503375, 47.07087689, 47.34672002, 47.62256315, 47.89840629, 48.17424942, 48.45009255, 48.72593568, 49.00177882, 49.27762195, 49.55346508, 49.82930822, 50.10515135, 50.38099448, 50.65683762, 50.93268075, 51.20852388, 51.48436702, 51.76021015, 52.03605328, 52.31189641, 52.58773955, 52.86358268, 53.13942581, 53.41526895, 53.69111208, 53.96695521, 54.24279835, 54.51864148, 54.79448461, 55.07032775, 55.34617088, 55.62201401, 55.89785714, 56.17370028, 56.44954341, 56.72538654, 57.00122968, 57.27707281, 57.55291594, 57.82875908, 58.10460221, 58.38044534, 58.65628848, 58.93213161, 59.20797474, 59.48381787, 59.75966101, 60.03550414, 60.31134727, 60.58719041, 60.86303354, 61.13887667, 61.41471981, 61.69056294, 61.96640607, 62.24224921, 62.51809234, 62.79393547, 63.0697786, 63.34562174, 63.62146487, 63.897308, 64.17315114, 64.44899427, 64.7248374, 65.00068054, 65.27652367, 65.5523668, 65.82820994, 66.10405307, 66.3798962, 66.65573933, 66.93158247, 67.2074256, 67.48326873, 67.75911187, 68.034955, 68.31079813, 68.58664127, 68.8624844, 69.13832753, 69.41417067, 69.6900138, 69.96585693, 70.24170006, 70.5175432, 70.79338633, 71.06922946, 71.3450726, 71.62091573, 71.89675886, 72.172602, 72.44844513])
    male_ok_y = np.array([4.65232456e-06, 1.01575006e-05, 2.1133468e-05, 4.19506031e-05, 7.95519137e-05, 0.000144313592, 0.000250803873, 0.000418187606, 0.000669969982, 0.00103277765, 0.00153396704, 0.00219804727, 0.00304220635, 0.00407159513, 0.00527536019, 0.00662458398, 0.00807314371, 0.00956196864, 0.0110263338, 0.0124049197, 0.0136487259, 0.0147278479, 0.0156346929, 0.0163832578, 0.0170052052, 0.0175441993, 0.0180500072, 0.0185732607, 0.0191608851, 0.01985158, 0.0206708066, 0.0216255342, 0.0227000939, 0.0238551713, 0.0250316597, 0.0261596958, 0.0271712556, 0.0280131163, 0.0286565948, 0.0291014911, 0.0293736126, 0.02951724, 0.0295850745, 0.0296282857, 0.0296885077, 0.0297926169, 0.0299503893, 0.0301548426, 0.0303850266, 0.0306109229, 0.0307997794, 0.0309227495, 0.0309604362, 0.0309061188, 0.030766094, 0.0305574266, 0.0303041099, 0.0300328788, 0.0297696731, 0.0295372154, 0.0293536417, 0.0292318317, 0.029179082, 0.0291969573, 0.0292813815, 0.0294231588, 0.0296090835, 0.0298236215, 0.0300509041, 0.0302765862, 0.0304890852, 0.0306798892, 0.0308429638, 0.0309736465, 0.0310676479, 0.0311207285, 0.0311293052, 0.0310917849, 0.0310100254, 0.0308901944, 0.0307424858, 0.0305795921, 0.0304143164, 0.0302570292, 0.0301137072, 0.0299850456, 0.0298667357, 0.0297506319, 0.0296263356, 0.0294827436, 0.0293093025, 0.0290969516, 0.0288389031, 0.0285314202, 0.0281746218, 0.0277731447, 0.027336347, 0.0268777384, 0.0264134896, 0.0259601605, 0.0255320802, 0.0251389951, 0.0247845952, 0.0244663298, 0.0241765763, 0.0239048536, 0.0236404794, 0.0233749716, 0.0231036012, 0.0228258038, 0.0225445094, 0.0222647567, 0.021992099, 0.0217312716, 0.0214854256, 0.021256021, 0.0210432844, 0.0208470153, 0.0206674689, 0.0205060409, 0.0203655376, 0.0202499001, 0.0201633742, 0.0201092278, 0.0200882375, 0.0200972644, 0.0201283157, 0.0201684837, 0.0202010192, 0.0202075131, 0.0201707942, 0.0200778604, 0.0199220734, 0.0197040442, 0.0194310295, 0.0191150872, 0.0187705353, 0.0184113393, 0.0180489683, 0.0176911007, 0.0173413935, 0.0170003544, 0.0166671215, 0.0163416613, 0.0160266337, 0.0157281216, 0.0154547034, 0.0152149494, 0.015014114, 0.0148512525, 0.0147179583, 0.0145993624, 0.014477201, 0.0143340063, 0.0141571242, 0.0139414133, 0.0136899857, 0.0134129652, 0.0131247249, 0.0128403281, 0.0125719512, 0.0123259823, 0.0121013159, 0.0118891211, 0.0116740737, 0.0114367693, 0.0111568431, 0.0108162726, 0.0104023883, 0.00991020961, 0.00934378646, 0.00871626333, 0.00804847594, 0.00736610641, 0.00669576213, 0.00606069628, 0.00547709601, 0.00495181188, 0.00448208267, 0.00405731989, 0.00366250257, 0.00328233561, 0.00290514473, 0.00252556754, 0.00214544246, 0.00177280615, 0.00141943447, 0.00109772928, 0.000817846092, 0.000585763223, 0.000402611138, 0.000265169409, 0.000167142209, 0.000100714424, 5.79571874e-05, 3.18227833e-05, 1.66578765e-05, 8.30639759e-06, 3.94276874e-06, 1.78029025e-06])
    male_fail_x = np.array([15.8862862, 16.17776506, 16.46924392, 16.76072277, 17.05220163, 17.34368049, 17.63515935, 17.92663821, 18.21811706, 18.50959592, 18.80107478, 19.09255364, 19.3840325, 19.67551135, 19.96699021, 20.25846907, 20.54994793, 20.84142679, 21.13290564, 21.4243845, 21.71586336, 22.00734222, 22.29882108, 22.59029994, 22.88177879, 23.17325765, 23.46473651, 23.75621537, 24.04769423, 24.33917308, 24.63065194, 24.9221308, 25.21360966, 25.50508852, 25.79656737, 26.08804623, 26.37952509, 26.67100395, 26.96248281, 27.25396167, 27.54544052, 27.83691938, 28.12839824, 28.4198771, 28.71135596, 29.00283481, 29.29431367, 29.58579253, 29.87727139, 30.16875025, 30.4602291, 30.75170796, 31.04318682, 31.33466568, 31.62614454, 31.91762339, 32.20910225, 32.50058111, 32.79205997, 33.08353883, 33.37501769, 33.66649654, 33.9579754, 34.24945426, 34.54093312, 34.83241198, 35.12389083, 35.41536969, 35.70684855, 35.99832741, 36.28980627, 36.58128512, 36.87276398, 37.16424284, 37.4557217, 37.74720056, 38.03867941, 38.33015827, 38.62163713, 38.91311599, 39.20459485, 39.49607371, 39.78755256, 40.07903142, 40.37051028, 40.66198914, 40.953468, 41.24494685, 41.53642571, 41.82790457, 42.11938343, 42.41086229, 42.70234114, 42.99382, 43.28529886, 43.57677772, 43.86825658, 44.15973544, 44.45121429, 44.74269315, 45.03417201, 45.32565087, 45.61712973, 45.90860858, 46.20008744, 46.4915663, 46.78304516, 47.07452402, 47.36600287, 47.65748173, 47.94896059, 48.24043945, 48.53191831, 48.82339716, 49.11487602, 49.40635488, 49.69783374, 49.9893126, 50.28079146, 50.57227031, 50.86374917, 51.15522803, 51.44670689, 51.73818575, 52.0296646, 52.32114346, 52.61262232, 52.90410118, 53.19558004, 53.48705889, 53.77853775, 54.07001661, 54.36149547, 54.65297433, 54.94445319, 55.23593204, 55.5274109, 55.81888976, 56.11036862, 56.40184748, 56.69332633, 56.98480519, 57.27628405, 57.56776291, 57.85924177, 58.15072062, 58.44219948, 58.73367834, 59.0251572, 59.31663606, 59.60811491, 59.89959377, 60.19107263, 60.48255149, 60.77403035, 61.06550921, 61.35698806, 61.64846692, 61.93994578, 62.23142464, 62.5229035, 62.81438235, 63.10586121, 63.39734007, 63.68881893, 63.98029779, 64.27177664, 64.5632555, 64.85473436, 65.14621322, 65.43769208, 65.72917093, 66.02064979, 66.31212865, 66.60360751, 66.89508637, 67.18656523, 67.47804408, 67.76952294, 68.0610018, 68.35248066, 68.64395952, 68.93543837, 69.22691723, 69.51839609, 69.80987495, 70.10135381, 70.39283266, 70.68431152, 70.97579038, 71.26726924, 71.5587481, 71.85022696, 72.14170581, 72.43318467, 72.72466353, 73.01614239, 73.30762125, 73.5991001, 73.89057896])
    male_fail_y = np.array([8.29984255e-06, 1.47809259e-05, 2.56782828e-05, 4.35273563e-05, 7.20098938e-05, 0.000116294488, 0.000183386953, 0.000282440536, 0.000424955698, 0.000624783036, 0.000897836862, 0.00126143753, 0.00173323277, 0.00232970413, 0.00306434076, 0.00394564914, 0.0049752489, 0.00614636063, 0.00744300305, 0.00884016952, 0.0103051436, 0.0117999521, 0.0132847634, 0.0147218581, 0.0160796593, 0.0173362485, 0.0184818253, 0.0195196948, 0.02046557, 0.021345219, 0.0221907407, 0.023035959, 0.0239115747, 0.0248407585, 0.0258358149, 0.026896393, 0.0280094869, 0.0291511875, 0.0302898754, 0.0313903198, 0.0324180186, 0.0333431124, 0.034143319, 0.0348055469, 0.035326108, 0.0357096951, 0.0359674834, 0.0361148086, 0.0361688658, 0.0361467852, 0.0360642915, 0.035935, 0.0357702657, 0.0355794191, 0.0353701917, 0.0351491556, 0.03492206, 0.0346940113, 0.0344695042, 0.0342523459, 0.0340455299, 0.0338511055, 0.0336700745, 0.0335023333, 0.0333466664, 0.0332008043, 0.0330615523, 0.0329249983, 0.0327867926, 0.0326424771, 0.0324878234, 0.0323191358, 0.0321334791, 0.0319288117, 0.031704026, 0.0314589174, 0.0311941097, 0.0309109567, 0.0306114299, 0.0302979864, 0.0299734095, 0.0296406232, 0.0293024934, 0.0289616446, 0.0286203238, 0.0282803335, 0.0279430364, 0.0276094103, 0.0272801201, 0.0269555719, 0.026635932, 0.0263211195, 0.0260107997, 0.0257044198, 0.0254013091, 0.0251008471, 0.0248026629, 0.0245068097, 0.0242138522, 0.0239248252, 0.023641058, 0.0233639032, 0.0230944416, 0.0228332418, 0.0225802425, 0.0223347862, 0.0220957925, 0.0218620224, 0.0216323671, 0.021406096, 0.0211830178, 0.0209635348, 0.0207485945, 0.0205395543, 0.0203379845, 0.0201454228, 0.0199631, 0.0197916491, 0.0196308248, 0.0194792688, 0.0193343686, 0.0191922564, 0.0190479803, 0.0188958535, 0.0187299494, 0.0185446798, 0.0183353671, 0.0180987234, 0.0178331628, 0.0175389067, 0.0172178823, 0.0168734478, 0.0165100029, 0.0161325512, 0.0157462734, 0.0153561557, 0.0149666967, 0.0145816982, 0.0142041305, 0.0138360622, 0.0134786382, 0.0131321008, 0.012795853, 0.0124685679, 0.0121483538, 0.0118329776, 0.0115201427, 0.0112078009, 0.0108944648, 0.0105794733, 0.0102631575, 0.00994686184, 0.00963279255, 0.00932369433, 0.00902238845, 0.00873123711, 0.0084516193, 0.00818351052, 0.0079252476, 0.00767353358, 0.00742370002, 0.00717020187, 0.0069072814, 0.00662970844, 0.00633348934, 0.0060164391, 0.00567852942, 0.00532195801, 0.00495092685, 0.00457116263, 0.00418925485, 0.00381191675, 0.00344528664, 0.00309437716, 0.00276274962, 0.00245244494, 0.00216415216, 0.00189755122, 0.00165173887, 0.00142564075, 0.00121832903, 0.00102919733, 0.000857983591, 0.000704667137, 0.000569289852, 0.000451759435, 0.000351686079, 0.000268286546, 0.000200368126, 0.000146385143, 0.000104546894, 7.29498825e-05, 4.97083732e-05, 3.30635695e-05, 2.14602297e-05, 1.35879192e-05, 8.39056303e-06, 5.05181068e-06, 2.96502978e-06, 1.69610665e-06])
    
    female_ok_x = np.array([17.33141439, 17.60739252, 17.88337066, 18.15934879, 18.43532693, 18.71130507, 18.9872832, 19.26326134, 19.53923947, 19.81521761, 20.09119574, 20.36717388, 20.64315202, 20.91913015, 21.19510829, 21.47108642, 21.74706456, 22.02304269, 22.29902083, 22.57499896, 22.8509771, 23.12695524, 23.40293337, 23.67891151, 23.95488964, 24.23086778, 24.50684591, 24.78282405, 25.05880218, 25.33478032, 25.61075846, 25.88673659, 26.16271473, 26.43869286, 26.714671, 26.99064913, 27.26662727, 27.5426054, 27.81858354, 28.09456168, 28.37053981, 28.64651795, 28.92249608, 29.19847422, 29.47445235, 29.75043049, 30.02640862, 30.30238676, 30.5783649, 30.85434303, 31.13032117, 31.4062993, 31.68227744, 31.95825557, 32.23423371, 32.51021184, 32.78618998, 33.06216812, 33.33814625, 33.61412439, 33.89010252, 34.16608066, 34.44205879, 34.71803693, 34.99401506, 35.2699932, 35.54597134, 35.82194947, 36.09792761, 36.37390574, 36.64988388, 36.92586201, 37.20184015, 37.47781828, 37.75379642, 38.02977456, 38.30575269, 38.58173083, 38.85770896, 39.1336871, 39.40966523, 39.68564337, 39.96162151, 40.23759964, 40.51357778, 40.78955591, 41.06553405, 41.34151218, 41.61749032, 41.89346845, 42.16944659, 42.44542473, 42.72140286, 42.997381, 43.27335913, 43.54933727, 43.8253154, 44.10129354, 44.37727167, 44.65324981, 44.92922795, 45.20520608, 45.48118422, 45.75716235, 46.03314049, 46.30911862, 46.58509676, 46.86107489, 47.13705303, 47.41303117, 47.6890093, 47.96498744, 48.24096557, 48.51694371, 48.79292184, 49.06889998, 49.34487811, 49.62085625, 49.89683439, 50.17281252, 50.44879066, 50.72476879, 51.00074693, 51.27672506, 51.5527032, 51.82868133, 52.10465947, 52.38063761, 52.65661574, 52.93259388, 53.20857201, 53.48455015, 53.76052828, 54.03650642, 54.31248455, 54.58846269, 54.86444083, 55.14041896, 55.4163971, 55.69237523, 55.96835337, 56.2443315, 56.52030964, 56.79628777, 57.07226591, 57.34824405, 57.62422218, 57.90020032, 58.17617845, 58.45215659, 58.72813472, 59.00411286, 59.28009099, 59.55606913, 59.83204727, 60.1080254, 60.38400354, 60.65998167, 60.93595981, 61.21193794, 61.48791608, 61.76389422, 62.03987235, 62.31585049, 62.59182862, 62.86780676, 63.14378489, 63.41976303, 63.69574116, 63.9717193, 64.24769744, 64.52367557, 64.79965371, 65.07563184, 65.35160998, 65.62758811, 65.90356625, 66.17954438, 66.45552252, 66.73150066, 67.00747879, 67.28345693, 67.55943506, 67.8354132, 68.11139133, 68.38736947, 68.6633476, 68.93932574, 69.21530388, 69.49128201, 69.76726015, 70.04323828, 70.31921642, 70.59519455, 70.87117269, 71.14715082, 71.42312896, 71.6991071, 71.97508523, 72.25106337])
    female_ok_y = np.array([1.23098564e-06, 3.1499355e-06, 7.56956726e-06, 1.70940064e-05, 3.63053966e-05, 7.25913876e-05, 0.000136808502, 0.000243385004, 0.000409442804, 0.000652708617, 0.000988400076, 0.00142577129, 0.00196532391, 0.0025976032, 0.0033039806, 0.00405912344, 0.00483434526, 0.0056009671, 0.00633314418, 0.00701002853, 0.00761735531, 0.00814849504, 0.00860488329, 0.00899574728, 0.00933725773, 0.00965147948, 0.00996551868, 0.0103109291, 0.0107228597, 0.0112379448, 0.011889954, 0.0127029639, 0.013683153, 0.0148117171, 0.016042077, 0.0173038726, 0.0185141484, 0.0195933671, 0.0204816962, 0.0211505249, 0.0216057338, 0.0218821759, 0.0220318142, 0.0221097497, 0.0221623838, 0.0222204616, 0.0222976091, 0.0223931441, 0.0224970601, 0.0225952222, 0.0226736011, 0.0227212376, 0.0227321207, 0.0227062036, 0.0226495711, 0.0225736419, 0.0224934147, 0.0224250869, 0.0223836681, 0.0223812555, 0.0224263908, 0.022524465, 0.022678702, 0.0228910103, 0.0231620643, 0.0234903577, 0.0238705351, 0.0242918128, 0.0247374843, 0.0251862017, 0.0256150131, 0.0260033174, 0.0263364029, 0.0266073412, 0.026816686, 0.0269703437, 0.0270766557, 0.0271438379, 0.027178466, 0.0271850294, 0.0271661286, 0.0271228994, 0.0270555691, 0.0269643055, 0.0268504309, 0.0267176871, 0.026572894, 0.0264253786, 0.0262850193, 0.0261594046, 0.0260510918, 0.0259560439, 0.0258640109, 0.0257610169, 0.0256333949, 0.0254721707, 0.025276291, 0.0250534297, 0.0248179247, 0.0245865192, 0.0243735061, 0.0241871113, 0.0240283636, 0.0238925634, 0.0237723599, 0.0236609098, 0.0235538207, 0.0234493667, 0.0233473567, 0.0232475966, 0.0231488967, 0.0230491296, 0.0229462252, 0.0228395317, 0.0227308975, 0.0226250851, 0.0225295108, 0.02245353, 0.022407473, 0.0224014895, 0.0224442232, 0.0225414966, 0.0226954094, 0.0229042529, 0.0231632902, 0.0234659251, 0.0238044642, 0.0241698676, 0.0245505251, 0.0249308154, 0.025290577, 0.0256064356, 0.0258552682, 0.0260192078, 0.0260907789, 0.0260763023, 0.0259958822, 0.0258792443, 0.0257582426, 0.0256583901, 0.0255924823, 0.0255587487, 0.0255441433, 0.0255312263, 0.0255056458, 0.025461184, 0.0254006038, 0.0253324272, 0.0252653763, 0.0252028957, 0.0251398461, 0.0250624513, 0.0249514129, 0.0247871707, 0.0245557526, 0.0242535233, 0.023889383, 0.0234835884, 0.0230633127, 0.0226561136, 0.0222832583, 0.0219549569, 0.0216688331, 0.0214116504, 0.0211630157, 0.0208991624, 0.0205953367, 0.0202265535, 0.0197678352, 0.0191956319, 0.0184914882, 0.0176474686, 0.0166712854, 0.0155885112, 0.0144400975, 0.0132752548, 0.01214158, 0.011075305, 0.0100944066, 0.00919638687, 0.008361265, 0.00755903154, 0.00675964129, 0.00594279105, 0.00510460342, 0.00425919622, 0.00343480574, 0.00266600345, 0.00198477608, 0.00141331683, 0.000960379836, 0.000621550509, 0.000382476288, 0.000223444367, 0.000123756706, 6.48997204e-05, 3.21860903e-05, 1.50784022e-05, 6.66573487e-06, 2.77794942e-06])
    female_fail_x = np.array([15.79818607, 16.09133457, 16.38448306, 16.67763156, 16.97078005, 17.26392855, 17.55707704, 17.85022554, 18.14337403, 18.43652253, 18.72967102, 19.02281952, 19.31596801, 19.60911651, 19.902265, 20.1954135, 20.48856199, 20.78171049, 21.07485898, 21.36800748, 21.66115597, 21.95430447, 22.24745296, 22.54060146, 22.83374995, 23.12689845, 23.42004694, 23.71319544, 24.00634393, 24.29949243, 24.59264092, 24.88578942, 25.17893791, 25.47208641, 25.7652349, 26.0583834, 26.35153189, 26.64468039, 26.93782888, 27.23097738, 27.52412587, 27.81727437, 28.11042286, 28.40357136, 28.69671985, 28.98986835, 29.28301684, 29.57616534, 29.86931383, 30.16246233, 30.45561082, 30.74875932, 31.04190781, 31.33505631, 31.6282048, 31.9213533, 32.21450179, 32.50765029, 32.80079878, 33.09394728, 33.38709577, 33.68024427, 33.97339276, 34.26654126, 34.55968975, 34.85283825, 35.14598674, 35.43913524, 35.73228373, 36.02543223, 36.31858072, 36.61172922, 36.90487771, 37.19802621, 37.4911747, 37.7843232, 38.07747169, 38.37062019, 38.66376868, 38.95691718, 39.25006568, 39.54321417, 39.83636267, 40.12951116, 40.42265966, 40.71580815, 41.00895665, 41.30210514, 41.59525364, 41.88840213, 42.18155063, 42.47469912, 42.76784762, 43.06099611, 43.35414461, 43.6472931, 43.9404416, 44.23359009, 44.52673859, 44.81988708, 45.11303558, 45.40618407, 45.69933257, 45.99248106, 46.28562956, 46.57877805, 46.87192655, 47.16507504, 47.45822354, 47.75137203, 48.04452053, 48.33766902, 48.63081752, 48.92396601, 49.21711451, 49.510263, 49.8034115, 50.09655999, 50.38970849, 50.68285698, 50.97600548, 51.26915397, 51.56230247, 51.85545096, 52.14859946, 52.44174795, 52.73489645, 53.02804494, 53.32119344, 53.61434193, 53.90749043, 54.20063892, 54.49378742, 54.78693591, 55.08008441, 55.3732329, 55.6663814, 55.95952989, 56.25267839, 56.54582688, 56.83897538, 57.13212387, 57.42527237, 57.71842086, 58.01156936, 58.30471785, 58.59786635, 58.89101484, 59.18416334, 59.47731183, 59.77046033, 60.06360882, 60.35675732, 60.64990581, 60.94305431, 61.2362028, 61.5293513, 61.82249979, 62.11564829, 62.40879678, 62.70194528, 62.99509377, 63.28824227, 63.58139076, 63.87453926, 64.16768775, 64.46083625, 64.75398474, 65.04713324, 65.34028173, 65.63343023, 65.92657872, 66.21972722, 66.51287571, 66.80602421, 67.0991727, 67.3923212, 67.68546969, 67.97861819, 68.27176668, 68.56491518, 68.85806367, 69.15121217, 69.44436066, 69.73750916, 70.03065765, 70.32380615, 70.61695464, 70.91010314, 71.20325163, 71.49640013, 71.78954862, 72.08269712, 72.37584561, 72.66899411, 72.9621426, 73.2552911, 73.54843959, 73.84158809, 74.13473658])
    female_fail_y = np.array([1.12993143e-05, 1.96313389e-05, 3.32565407e-05, 5.49448958e-05, 8.85525678e-05, 0.000139253423, 0.000213725518, 0.000320239958, 0.000468591934, 0.000669815437, 0.000935637902, 0.00127766075, 0.00170629531, 0.00222953587, 0.00285170379, 0.00357233791, 0.00438542433, 0.00527914621, 0.00623628561, 0.00723533071, 0.00825224132, 0.00926272153, 0.0102447568, 0.0111811114, 0.0120614625, 0.0128838695, 0.0136553467, 0.0143914018, 0.0151145259, 0.0158517447, 0.0166314608, 0.0174799228, 0.0184177273, 0.0194567921, 0.0205982164, 0.0218313549, 0.0231342918, 0.0244757039, 0.0258178947, 0.0271205883, 0.028344942, 0.0294572028, 0.0304314997, 0.0312514332, 0.0319103479, 0.0324104121, 0.0327608233, 0.0329755692, 0.0330711902, 0.033064907, 0.032973336, 0.0328118526, 0.032594513, 0.0323343491, 0.032043811, 0.0317351507, 0.0314206001, 0.0311122794, 0.0308218454, 0.0305599518, 0.0303356271, 0.0301556785, 0.0300242151, 0.0299423549, 0.0299081463, 0.0299167049, 0.0299605499, 0.0300301071, 0.0301143454, 0.0302015036, 0.0302798622, 0.0303385044, 0.0303680068, 0.0303609947, 0.0303125092, 0.0302201513, 0.0300839966, 0.0299063085, 0.0296911041, 0.0294436437, 0.0291699159, 0.0288761769, 0.0285685775, 0.0282528875, 0.0279343016, 0.0276173036, 0.0273055611, 0.0270018336, 0.0267078917, 0.0264244576, 0.0261511885, 0.0258867228, 0.0256288065, 0.0253744993, 0.0251204472, 0.0248631968, 0.0245995174, 0.0243267004, 0.0240428089, 0.0237468628, 0.0234389495, 0.0231202561, 0.022793018, 0.022460383, 0.0221261898, 0.0217946734, 0.0214701232, 0.0211565373, 0.0208573257, 0.0205751165, 0.0203117027, 0.0200681374, 0.0198449532, 0.019642449, 0.0194609691, 0.0193010976, 0.0191637113, 0.0190498613, 0.0189604928, 0.0188960469, 0.0188560125, 0.0188385149, 0.0188400257, 0.0188552709, 0.0188773873, 0.018898344, 0.0189096017, 0.0189029364, 0.0188713137, 0.0188096797, 0.0187155353, 0.0185891917, 0.0184336645, 0.0182542269, 0.0180577107, 0.0178516843, 0.0176436478, 0.0174403642, 0.0172473979, 0.0170688751, 0.0169074322, 0.0167642916, 0.0166394007, 0.016531587, 0.0164387141, 0.0163578426, 0.0162854149, 0.0162174744, 0.0161499124, 0.0160787122, 0.0160001454, 0.0159108728, 0.0158079183, 0.0156885117, 0.0155498293, 0.0153886899, 0.0152012815, 0.0149829962, 0.0147284358, 0.0144316263, 0.0140864445, 0.0136872239, 0.013229474, 0.0127106203, 0.0121306587, 0.0114926156, 0.0108027263, 0.010070274, 0.00930708439, 0.00852672259, 0.00774349177, 0.00697136885, 0.00622302455, 0.00550905937, 0.00483754494, 0.00421390207, 0.00364108503, 0.00311999128, 0.00264998696, 0.00222943654, 0.00185614668, 0.00152767208, 0.00124147272, 0.000994947956, 0.000785394287, 0.000609939639, 0.000465498159, 0.000348772318, 0.000256309185, 0.000184600983, 0.000130209648, 8.98921225e-05, 6.07062382e-05, 4.0084032e-05, 2.58674644e-05, 1.63087033e-05, 1.00420878e-05, 6.03722841e-06, 3.54276059e-06, 2.0287462e-06])
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15,6), sharey=True)

    # CAUTION: somehow for the male the traget 0 and 1 are inversed! that's why I switch colors here
    fig, (ax_male, ax_female) = plt.subplots(1, 2, figsize=(15,6), sharey=True)

    # CAUTION: somehow for the male the traget 0 and 1 are inversed! that's why I switch colors here

    ax_male.set_title('Male gender')
    ax_male.set_xlabel('Years birth')
    ax_male.set_ylabel('Density')
    ax_male.legend()

    ax_female.set_title('Female gender')
    ax_female.set_xlabel('Years birth')
    ax_female.legend()

    ax_male.plot(male_fail_x, male_fail_y, 'tab:blue', label='Target0')
    ax_male.plot(male_ok_x, male_ok_y, 'tab:orange', label='Target1')
    ax_female.plot(female_ok_x, female_ok_y, label='Target0')
    ax_female.plot(female_fail_x, female_fail_y, label='Target1')
    if CODE_GENDER == 'M':
        ax_male.axvline(DAYS_BIRTH / 365.25, 0.05, 0.95, color='tab:green')
    if CODE_GENDER == 'F':
        ax_female.axvline(DAYS_BIRTH / 365.25, 0.05, 0.95, color='tab:green')
    
    st.pyplot(fig)
    
    test_columntransformer = joblib.load('credit_scoring_transformer.pkl')
    X_test_trfm = test_columntransformer.transform(data_for_shap)
    st.write('Shape of data for shap:', X_test_trfm.shape)
    shap_feature_names = test_columntransformer.get_feature_names_out()
#    st.write(shap_feature_names.shape)
#    st.write(shap_feature_names)
    linear_explainer = joblib.load(filename='explainer.bz2')
    shap_vals = linear_explainer.shap_values(X_test_trfm[0])
    st.write("Prediction From Adding SHAP Values to Base Value:", linear_explainer.expected_value + shap_vals.sum())
    
    fig_shap = plt.figure()
    st.pyplot(fig_shap, shap.decision_plot(linear_explainer.expected_value,
                   linear_explainer.shap_values(X_test_trfm[0]),
#                    feature_names=shap_feature_names, # TypeError: The feature_names arg requires a list or numpy array.
                     feature_names=shap_feature_names.tolist(), #AttributeError: 'list' object has no attribute 'tolist'
#                   matplotlib=True # https://discuss.streamlit.io/t/shap-shap-force-plot-on-streamlit/10071/2  Oct '21
                   ))
# another workaround see on https://gist.github.com/andfanilo/6bad569e3405c89b6db1df8acf18df0e   
# another workaround see on https://discuss.streamlit.io/t/display-shap-diagrams-with-streamlit/1029/9

if __name__ == '__main__':
    main()
