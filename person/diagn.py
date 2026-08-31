import pandas as pd

df = pd.read_csv(
    "test_Applikationsprofil_person.csv",
    dtype=str
)

print(df.columns.tolist())