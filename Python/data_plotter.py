import pandas as pd

saba_data_path = 'collected_data/saba_2541/received_data_Saba_2541.csv'

df_saba = pd.read_csv(saba_data_path)
print(df_saba.head)




