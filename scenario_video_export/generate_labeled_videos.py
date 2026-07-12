# load labeled_scenario.json 
# and generate relative videos 


import ujson
import numpy as np 
import cv2 
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

def draw_rotated_bbox(img, x, y, width, length, heading, color=(0,255,0), thickness=2):
    # 建立 bbox 四個角的座標（以中心為原點）
    box = np.array([
        [-length/2, -width/2],
        [-length/2,  width/2],
        [ length/2,  width/2],
        [ length/2, -width/2]
    ])
    # 旋轉
    theta = np.deg2rad(-heading)
    rot = np.array([
        [np.cos(theta), -np.sin(theta)],
        [np.sin(theta),  np.cos(theta)]
    ])
    box = box @ rot.T
    # 平移到 (x, y)
    box += np.array([x, y])
    # 轉成 int
    box = box.astype(int)
    # 畫多邊形
    # cv2.polylines(img, [box], isClosed=True, color=color, thickness=thickness)

    cv2.fillPoly(img, [box], color=color)


ortho_px_to_meter = 0.0499967249445942

root_path = "../data"
labeled_scenario_path = f"{root_path}/labeled_scenarios.json"



labeled_scenario_data = ujson.load(open(labeled_scenario_path, "r"))
image_background = cv2.imread(f"{root_path}/00_background.png")
with open(f'{root_path}/track_frame_dict.json', 'r', encoding='utf-8') as f:
    track_dict = ujson.load(f)


# idx_to_label = {
#     0: "None",
#     1: "直行 + 左轉",
#     2: "左轉 + 直行",
#     3: "並行 機車加速通過",
#     4: "並行 機車等速通過",
#     5: "並行 機車減速",
#     6: "繞過前方車輛",
#     7: "被 右側 cut-in",
#     8: "被 左側 cut-in",
#     9: "右轉 + 機車直行與待轉",
#     10: "左轉 + 機車待轉",
#     11: "右轉 + 行人通過",
#     12: "左轉 + 行人通過",
#     13: "不確定"
# }
# English translation of idx_to_label
idx_to_label = {
    0: "None",
    1: "Going straight + Left turn",
    2: "Left turn + Going straight",
    3: "Parallel : motorcycle accelerates through",
    4: "Parallel : motorcycle passes at constant speed",
    5: "Parallel : motorcycle decelerates",
    6: "Bypass the vehicle ahead",
    7: "Cut-in from the right",
    8: "Cut-in from the left",
    9: "Right turn + motorcycle going straight and waiting to turn",
    10: "Left turn + motorcycle waiting to turn",
    11: "Right turn + pedestrian crossing",
    12: "Left turn + pedestrian crossing",
    13: "Uncertain"
}




os.makedirs("./videos", exist_ok=True)

def process_scenario(scenario_key):
    labeled_scenario = labeled_scenario_data[scenario_key]

    ego_id = labeled_scenario["ego_id"]
    actor_id = labeled_scenario["actor_id"]
    min_frame = int(labeled_scenario["min_frame"])
    max_frame = int(labeled_scenario["max_frame"])
    label_idx = labeled_scenario["label_idx"]

    if label_idx == 0:
        return None

    video_name = f"{ego_id}_{actor_id}_{label_idx}.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    
    video = cv2.VideoWriter(f"./videos/{video_name}", fourcc, 60, (1730, 1030 ))


    



    for frame_num in range(min_frame, max_frame + 1):
        current_frame = str(frame_num)
        frame = image_background.copy()

        # draw ego 

        try:
            row = track_dict[ego_id][current_frame][0]
            x = row['xCenter'] / ortho_px_to_meter
            y = -row['yCenter'] / ortho_px_to_meter
            heading = row['heading']
            width = row['width'] / ortho_px_to_meter
            length = row['length'] / ortho_px_to_meter
            draw_rotated_bbox(frame, x, y, width, length, heading, color=(0,255,0))

        except:
            pass

        # draw actor 
        try:
            row = track_dict[actor_id][current_frame][0]
            x = row['xCenter'] / ortho_px_to_meter
            y = -row['yCenter'] / ortho_px_to_meter
            heading = row['heading']
            width = row['width'] / ortho_px_to_meter
            length = row['length'] / ortho_px_to_meter
            draw_rotated_bbox(frame, x, y, width, length, heading, color=(0,0,255))
        except:
            pass

        # write label to frame 
        cv2.putText(frame, f"Label: {idx_to_label[label_idx]}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 0, 0), 5)


        frame = cv2.resize(frame, (1730, 1030 ))

        video.write(frame)
    video.release()
    return video_name

# 平行處理所有 labeled scenarios
max_workers = os.cpu_count() or 4
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = {executor.submit(process_scenario, k): k for k in labeled_scenario_data}
    for fut in as_completed(futures):
        key = futures[fut]
        try:
            result = fut.result()
            print(f"Finished: {result} (scenario {key})")
        except Exception as e:
            print(f"Error processing {key}: {e}")