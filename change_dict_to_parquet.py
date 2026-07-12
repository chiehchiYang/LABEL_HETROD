# change xxx.json to xxx.parquet
import pandas as pd
import ujson


file_path = './data/track_dict.json'

with open(file_path, 'r', encoding='utf-8') as f:
    data = ujson.load(f)
# df = pd.DataFrame.from_dict(data, orient='index')
# df.to_parquet('./data/track_dict.parquet', index=True)
# print("track_dict 已儲存至 ./data/track_dict.parquet")



# how to load parquet
# df2 = pd.read_parquet('./data/track_dict.parquet')
# print(df2)
# print(df2.loc['1'])  # access trackId = 1