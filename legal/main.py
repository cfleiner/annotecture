import pandas as pd

df = pd.read_csv("hf://datasets/nguyenthanhasia/gdpr-cases/gdpr_formalization_good_samples.csv")

df.to_excel("gdpr_formalization_good_samples.xlsx", index=False)