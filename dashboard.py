import pandas as pd
import streamlit as st
import requests


def request_prediction(model_uri, data):
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

#    st.title('Prediction de default de credit')
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
                                   min_value=0., max_value=50000., value=0., step=1.)
    DAYS_EMPLOYED = st.number_input('How many days before the application the person started current employment: enter any positive float number',
                                   min_value=0., max_value=50000., value=0., step=1
    status_unique = ['0', '1', '2', '3', '4', '5', 'C', 'X']
    STATUS = st.selectbox('Status of Credit Bureau loan during the month: active, closed, DPD0-30. C means closed, X means status unknown, 0 means no DPD, 1 means maximal did during month between 1-30, 2 means DPD 31-60... 5 means DPD 120+ or sold or written off )', status_unique, index=7)
    credit_active_unique = ['Active', 'Bad_debt', 'Closed', 'Sold']
    CREDIT_ACTIVE = st.selectbox('Status of the Credit Bureau (CB) reported credits', ['No reported credits', *credit_active_unique]) # if there were no credits before or another issue
    credit_type_unique = ["Another_type_of_loan", "Cash_loan_(non-earmarked)", "Consumer_credit", "Credit_card", "Microloan", "Unknown_type_of_loan",]
    CREDIT_TYPE = st.selectbox('Type of Credit Bureau credit (Car, cash,...) For no reported credits select unknown type of loan', *credit_type_unique) # eventually I can fill all the columns with 0 when no reported credits. then I do as with CREDIT_ACTIVE
    FLAG_EMP_PHONE = st.number_input('Did client provide work phone (1=YES, 0=NO): enter 0 or 1',
                              min_value=0., max_value=1., value=0., step=1.)
    FLAG_WORK_PHONE = st.number_input('Did client provide home phone (1=YES, 0=NO): enter 0 or 1',
                              min_value=0., max_value=1., value=0., step=1.)
    FLAG_PHONE = st.number_input('Did client provide home phone (1=YES, 0=NO): enter 0 or 1',
                              min_value=0., max_value=1., value=0., step=1.)
    FLAG_PHONE = st.number_input('Did client provide work phone (1=YES, 0=NO): enter 0 or 1',
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
                              min_value=1., value=0., step=1.)
    CODE_GENDER = st.text_input('Gender of the client: please enter M for masculin or F for feminin', 'M')


    predict_btn = st.button('Predict')
    if predict_btn:
        columns = ["NAME_INCOME_TYPE", "AMT_ANNUITY", "EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3", "DAYS_EMPLOYED_PERC", "CREDIT_TERM", "STATUS_0_SUM", "STATUS_1_SUM", "STATUS_2_SUM", "STATUS_3_SUM", "STATUS_4_SUM", "STATUS_5_SUM", "STATUS_C_SUM", "STATUS_X_SUM", 
        "CREDIT_ACTIVE_Active_SUM", "CREDIT_ACTIVE_Bad_debt_SUM", "CREDIT_ACTIVE_Closed_SUM", "CREDIT_ACTIVE_Sold_SUM", "CREDIT_TYPE_Another_type_of_loan_SUM", "CREDIT_TYPE_Cash_loan_(non-earmarked)_SUM", "CREDIT_TYPE_Consumer_credit_SUM", "CREDIT_TYPE_Credit_card_SUM", "CREDIT_TYPE_Microloan_SUM", 
        "CREDIT_TYPE_Unknown_type_of_loan_SUM", "DAYS_BIRTH", "FLAG_EMP_PHONE", "FLAG_WORK_PHONE", "FLAG_PHONE", "REGION_RATING_CLIENT_W_CITY", "REG_CITY_NOT_LIVE_CITY", "REG_CITY_NOT_WORK_CITY", "LIVE_CITY_NOT_WORK_CITY", "FLAG_DOCUMENT_2", "FLAG_DOCUMENT_3", "FLAG_DOCUMENT_6", "FLAG_DOCUMENT_9", 
        "FLAG_DOCUMENT_13", "FLAG_DOCUMENT_14", "FLAG_DOCUMENT_16", "FLAG_DOCUMENT_21", "F_AGE", "M_AGE", "CNT_ADULTS"]
        data = [[NAME_INCOME_TYPE, AMT_ANNUITY, EXT_SOURCE_1, EXT_SOURCE_2, EXT_SOURCE_3, DAYS_EMPLOYED/DAYS_BIRTH, AMT_CREDIT/AMT_ANNUITY, *[int(i == STATUS) for i in status_unique], *[int(i==CREDIT_ACTIVE) for i in credit_active_unique], *[int(i==CREDIT_TYPE) for i in credit_type_unique], DAYS_BIRTH, 
        FLAG_EMP_PHONE, FLAG_WORK_PHONE, FLAG_PHONE, REGION_RATING_CLIENT_W_CITY, int(REG_CITY != LIVE_CITY), int(REG_CITY != WORK_CITY), int(LIVE_CITY != WORK_CITY) FLAG_DOCUMENT_2, FLAG_DOCUMENT_3, FLAG_DOCUMENT_6, FLAG_DOCUMENT_9, FLAG_DOCUMENT_13, FLAG_DOCUMENT_14, FLAG_DOCUMENT_16, FLAG_DOCUMENT_21, 
        DAYS_BIRTH if CODE_GENDER == 'F' else 0, DAYS_BIRTH if CODE_GENDER == 'M' else 0, CNT_FAM_MEMBERS - CNT_CHILDREN]]
        pred = None

  #      if api_choice == 'MLflow':
        pred = request_prediction(MLFLOW_URI, data)[0]
 #       elif api_choice == 'Cortex':
 #           pred = request_prediction(CORTEX_URI, data)[0]
  #      elif api_choice == 'Ray Serve':
   #         pred = request_prediction(RAY_SERVE_URI, columns, data)[0]
        st.write(
            'The predicted flag of the credit default is {:.1f}'.format(pred))


if __name__ == '__main__':
    main()
