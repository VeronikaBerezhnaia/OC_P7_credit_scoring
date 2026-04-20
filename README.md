# OC_P7_credit_scoring
You are a data scientist at a financial company called "Prêt à dépenser," which offers consumer loans to people with little or no credit history. The company wants to develop a scoring model to assess the probability of customer default to support the decision on whether or not to grant a loan to a potential customer, drawing on various data sources (behavioral data, data from other financial institutions, etc.). In addition, customer relationship managers have reported that customers are increasingly demanding transparency regarding credit approval decisions. This demand for transparency from customers is fully in line with the values the company seeks to embody. It therefore decided to develop an interactive dashboard so that customer relationship managers could both explain credit approval decisions as transparently as possible and allow their customers to access their personal information and explore it easily.

The raw data were taken from https://www.kaggle.com/c/home-credit-default-risk/data

Build a scoring model that automatically predicts the probability of a customer defaulting. Build an interactive dashboard for customer relationship managers that allows them to interpret the model’s predictions and improve customer relationship managers’ understanding of their clients. Your manager encourages you to select a Kaggle kernel to help you prepare the data needed to develop the scoring model. You will analyze this kernel and adapt it to ensure it meets the needs of your assignment. This will allow you to focus on developing the model, optimizing it, and understanding it.

Your manager has provided you with a set of specifications for the interactive dashboard. It must include at least the following features: 
- Display the score and an interpretation of that score for each client in a way that is understandable to someone without expertise in data science. 
- Display descriptive information about a client (via a filter system). 
- Compare descriptive information about a client to all clients or to a group of similar clients.

Expected deliverables
- The interactive dashboard that meets the specifications outlined above.
- A folder on GitHub with:
  - The modeling code (from preprocessing to prediction)
  - The code generating the dashboard
  - The code for deploying the model as an API
- A methodological note describing:
  - The model training methodology
  - The cost function, the optimization algorithm, and the evaluation metric
  - The model’s interpretability
  - Limitations and potential improvements
