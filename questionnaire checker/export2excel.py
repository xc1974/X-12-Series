import pandas as pd

def save_to_excel(data, output_path="results.xlsx"):
    df = pd.DataFrame(data)
    df.to_excel(output_path, index=False)

# 示例數據格式
data = {
    "Question 1": ["A"],
    "Question 2": ["B", "D"],
    # ...
}
save_to_excel(data)
