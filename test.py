import pandas as pd
import ujson 
import math

file_path = './data/00_pet_results_optimized.csv'
df = pd.read_csv(file_path)


result_dict = {}
for _, row in df.iterrows():
    key = f"{row['agent1_id']}_{row['agent2_id']}"
    pet = row['pet']
    # 檢查是否為無窮大
    if isinstance(pet, str):
        if pet.lower() == 'inf':
            # print(f"{key}: pet is string 'inf'")
            pet = 1000000
    elif isinstance(pet, float):
        if math.isinf(pet):
            # print(f"{key}: pet is float inf")
            pet = 1000000

    min_distance = row['min_distance']
    # 檢查是否為無窮大
    if isinstance(min_distance, str):
        if min_distance.lower() == 'inf':
            # print(f"{key}: min_distance is string 'inf'")
            min_distance = 1000000
    elif isinstance(min_distance, float):
        if math.isinf(min_distance):
            # print(f"{key}: min_distance is float inf")
            min_distance = 1000000

    


    result_dict[key] = {
        'pet': pet,
        'min_distance': min_distance
    }
    
with open('./data/pet_distance_dict.json', 'w', encoding='utf-8') as f:
    ujson.dump(result_dict, f, ensure_ascii=False, indent=2)

print("done")

# max_distance = max(
#     float(row['min_distance'])
#     for _, row in df.iterrows()
#     if str(row['min_distance']).lower() != 'inf'
# )
# print(f"max min_distance (不含 inf): {max_distance}")



# agent1_id, agent2_id, pet, min_distance
