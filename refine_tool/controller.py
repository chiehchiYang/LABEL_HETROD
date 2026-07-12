from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem, QMainWindow
from PyQt6.QtGui import QIcon, QFont

from video_controller import video_controller
import ujson
import os
from datetime import datetime


class MainWindow_controller(QMainWindow):
    def __init__(self, ui_class):
        super().__init__() 
        self.ui = ui_class()  # 使用傳入的 UI 類別
        self.ui.setupUi(self)

        # 根據 UI 模組決定 ToolTip 字體大小
        
        if "ui_ipad_mini" in ui_class.__module__.lower():
            self.setStyleSheet("QToolTip { font-size: 12pt; }")
        else:
            self.setStyleSheet("QToolTip { font-size: 24pt; }")


        self.data_path = "../data"

        # load trackid to class 
        with open(f'{self.data_path}/trackid_class.json', 'r', encoding='utf-8') as f:
            self.trackid_class = ujson.load(f)

        with open(f'{self.data_path}/pet_distance_dict.json', 'r', encoding='utf-8') as f:
            self.pet_min_distance_dict = ujson.load(f)

        with open(f'{self.data_path}/trackid_class.json', 'r', encoding='utf-8') as f:
            self.trackid_class = ujson.load(f)

        # load labeled scenarios 
        save_path = os.path.join(self.data_path, "labeled_scenarios.json")
        if os.path.exists(save_path):
            with open(save_path, "r", encoding="utf-8") as f:
                labeled_dict = ujson.load(f)
        else:
            return
        
        keys = list(labeled_dict.keys())

        self.ui.comboBox_ego_id.clear()
        for id in keys:
            # if "label_idx": 5
            if labeled_dict[id].get("label_idx", None) == 0:
                continue
            self.ui.comboBox_ego_id.addItem(id)
        self.current_id_pair = self.ui.comboBox_ego_id.currentText()

        self.video_controller = video_controller(data_path=self.data_path, ui=self.ui)
        self.label_tooltip_on = False  # 預設關閉

        self.ui.comboBox_ego_id.currentIndexChanged.connect(self.update_combobox_label_info)
        
        
        self.ui.pushButton_next_actor.clicked.connect(self.next_actor)

        self.ui.pushButton_label_notice_on.setText("開啟label 提示")
        self.ui.pushButton_label_notice_on.clicked.connect(self.toggle_label_tooltips)

        # 設定 label 按鈕點擊事件
        for i in range(0, 14):
            btn = getattr(self.ui, f"pushButton_label_{i}")
            btn.clicked.connect(lambda checked, idx=i: self.set_label_button_selected(idx))

        self.selected_label_btn_idx = None  # 記錄目前選中的 label 按鈕


        self.ui.pushButton_check_label_done.clicked.connect(self.save_current_checked)

        self.update_combobox_label_info()
    
    def toggle_label_tooltips(self):
        self.label_tooltip_on = not self.label_tooltip_on
        self.set_label_tooltips(enable=self.label_tooltip_on)
        if self.label_tooltip_on:
            self.ui.pushButton_label_notice_on.setText("關閉label 提示")
        else:
            self.ui.pushButton_label_notice_on.setText("開啟label 提示")

    def set_label_tooltips(self, enable=True):
        self.ui.pushButton_label_1.setToolTip("ego 路口直行，遇到對向左轉 \n{Car, Truck, Motor/Bike}" if enable else "")
        self.ui.pushButton_label_2.setToolTip("ego 路口左轉，遇到對向直行 \n{Car, Truck, Motor/Bike}" if enable else "")
        self.ui.pushButton_label_3.setToolTip("ego 與機踏車並行，機踏車加速通過" if enable else "")
        self.ui.pushButton_label_4.setToolTip("ego 與機踏車並行，機踏車等速並行" if enable else "")
        self.ui.pushButton_label_5.setToolTip("ego 與機踏車並行，機踏車減速" if enable else "")
        self.ui.pushButton_label_6.setToolTip("ego 前方同車道有停止車（等左轉/臨停）\n，ego 通過前未移動即算，需換道 (含佔用一點車道情況)，例：338,913,1096,1997" if enable else "")
        self.ui.pushButton_label_7.setToolTip("前方 {Car, Truck, Motor/Bike} 從右側 cut-in" if enable else "")
        self.ui.pushButton_label_8.setToolTip("前方 {Car, Truck, Motor/Bike} 從左側 cut-in" if enable else "")
        self.ui.pushButton_label_9.setToolTip("ego 右轉，右側機踏車直行通過（含待轉區）" if enable else "")
        self.ui.pushButton_label_10.setToolTip("ego 左轉，對向機踏車準備待轉" if enable else "")
        self.ui.pushButton_label_11.setToolTip("ego 右轉後遇見行人通過" if enable else "")
        self.ui.pushButton_label_12.setToolTip("ego 左轉後遇見行人通過" if enable else "")
        
    def update_combobox_label_info(self):




        # label_combobox_ego_id
        # x / x 
        total = self.ui.comboBox_ego_id.count()
        current_index = self.ui.comboBox_ego_id.currentIndex() + 1  # 1-based
        self.ui.label_combobox_ego_id.setText(f"{current_index} / {total}")

        self.video_controller.update_video_info()

        current_id_pair = self.ui.comboBox_ego_id.currentText()

        ego_id = current_id_pair.split("_")[0]
        other_actor_id = current_id_pair.split("_")[1]



        ##
        checked_list = []
        path = os.path.join(self.data_path, "label_check.txt")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                checked_list = f.read().splitlines()
        if current_id_pair in checked_list:
            self.ui.pushButton_check_label_done.setStyleSheet("color: red;")
        else:
            self.ui.pushButton_check_label_done.setStyleSheet("color: black;")


        # make this button to red after clicked
        # self.ui.pushButton_check_label_done.setStyleSheet("color: red;")

        # 讀取已標註 scenario
        save_path = os.path.join(self.data_path, "labeled_scenarios.json")
        selected_label_idx = None
        if os.path.exists(save_path):
            with open(save_path, "r", encoding="utf-8") as f:
                try:
                    labeled_dict = ujson.load(f)
                    if current_id_pair in labeled_dict:
                        selected_label_idx = labeled_dict[current_id_pair].get("label_idx", None)
                except Exception:
                    pass

        self.selected_label_btn_idx = selected_label_idx

        # 設定按鈕顏色
        car_truck_labels = [0, 1, 2, 6, 7, 8, 13]
        motor_bike_labels = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13]
        ped_labels = [0, 11, 12, 13]
        cls = self.trackid_class.get(str(other_actor_id), "unknown").lower()
        blue_labels = set()
        if cls in ["car", "truck"]:
            blue_labels = set(car_truck_labels)
        elif cls in ["motorcycle", "bicycle"]:
            blue_labels = set(motor_bike_labels)
        elif cls == "pedestrian":
            blue_labels = set(ped_labels)

        for i in range(0, 14):
            btn = getattr(self.ui, f"pushButton_label_{i}")
            if self.selected_label_btn_idx is not None and i == self.selected_label_btn_idx:
                btn.setStyleSheet("color: red;")
            elif i in blue_labels:
                btn.setStyleSheet("color: white;")
            else:
                btn.setStyleSheet("color: gray;")

        ## 
        # 取得 other actor class
        other_actor_class = self.trackid_class.get(str(other_actor_id), "unknown")
        # 取得 min_distance 和 PET
        min_distance = None
        pet = None
        key = f"{ego_id}_{other_actor_id}"
        if key in self.pet_min_distance_dict:
            min_distance = self.pet_min_distance_dict[key].get("min_distance", None)
            pet = self.pet_min_distance_dict[key].get("pet", None)
        # 判斷 pet 是否為 1000000
        pet_str = "inf" if pet == 1000000 else (pet if pet is not None else "N/A")

        def format_float(val):
            return f"{val:.2f}" if isinstance(val, (float, int)) and val is not None else "N/A"

        # 準備要顯示的資料
        data = [
            ("Ego ID", ego_id),
            ("Other Actor ID", other_actor_id),
            ("Class", other_actor_class),
            ("Min Distance", format_float(min_distance)),
            ("PET", f"{format_float(pet) if pet_str != 'inf' else 'inf'}\n"),
        ]


        # 設定 tableWidget 行數與列數
        self.ui.tableWidget_label_info.setRowCount(len(data))
        self.ui.tableWidget_label_info.setColumnCount(2)
        self.ui.tableWidget_label_info.setHorizontalHeaderLabels(["項目", "數值"])

        # 設定字體大小
        font = QFont()

        if "ui_ipad_mini" in self.ui.__module__.lower():
            font.setPointSize(10)
        else:
            font.setPointSize(16)

        # 填入資料
        for row, (label, value) in enumerate(data):
            item_label = QTableWidgetItem(str(label))
            item_label.setFont(font)
            item_value = QTableWidgetItem(str(value))
            item_value.setFont(font)
            self.ui.tableWidget_label_info.setItem(row, 0, item_label)
            self.ui.tableWidget_label_info.setItem(row, 1, item_value)

     
    def next_actor(self):
        
        current_index = self.ui.comboBox_ego_id.currentIndex()
        total = self.ui.comboBox_ego_id.count()
        if total == 0:
            return
        next_index = current_index + 1
        if next_index < total:
            self.ui.comboBox_ego_id.setCurrentIndex(next_index)
        else:
            self.ui.comboBox_ego_id.setCurrentIndex(0)

        
        self.video_controller.range_slider.setMinimum(0)
        self.video_controller.setslidervalue(0)
        self.video_controller.current_frame_no = 0

    def set_label_button_selected(self, selected_idx):
        

        id_pair = self.ui.comboBox_ego_id.currentText()
        ego_id, actor_id = id_pair.split("_")

        # 取得目前 class
        other_actor_class = actor_id
        other_actor_class = self.trackid_class.get(str(other_actor_class), "unknown").lower()
        car_truck_labels = [0, 1, 2, 6, 7, 8, 13]
        motor_bike_labels = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13]
        ped_labels = [0, 11, 12, 13]
        blue_labels = set()
        if other_actor_class in ["car", "truck"]:
            blue_labels = set(car_truck_labels)
        elif other_actor_class in ["motorcycle", "bicycle"]:
            blue_labels = set(motor_bike_labels)
        elif other_actor_class == "pedestrian":
            blue_labels = set(ped_labels)

        # 如果選到的按鈕不在對應 class 的範圍，直接忽略
        if selected_idx not in blue_labels:
            return

        for i in range(0, 14):
            btn = getattr(self.ui, f"pushButton_label_{i}")
            if i == selected_idx:
                btn.setStyleSheet("color: red;")
            elif i in blue_labels:
                btn.setStyleSheet("color: white;")
            else:
                btn.setStyleSheet("color: gray;")
        self.selected_label_btn_idx = selected_idx


        id = self.ui.comboBox_ego_id.currentText()

        ego_id, actor_id = id.split("_")
        
        min_frame, max_frame = self.video_controller.range_slider.value()  
        min_frame = self.video_controller.overlay_frame_list[min_frame]
        max_frame = self.video_controller.overlay_frame_list[max_frame]

        scenario = {
            "ego_id": ego_id,
            "actor_id": actor_id,
            "min_frame": min_frame,
            "max_frame": max_frame,
            "label_idx": selected_idx
        }
        key = f"{ego_id}_{actor_id}"

        # 儲存到 labeled_scenarios.json
        save_path = os.path.join(self.data_path, "labeled_scenarios.json")
        if os.path.exists(save_path):
            with open(save_path, "r", encoding="utf-8") as f:
                try:
                    labeled_dict = ujson.load(f)
                except Exception:
                    labeled_dict = {}
        else:
            labeled_dict = {}

        labeled_dict[key] = scenario

        with open(save_path, "w", encoding="utf-8") as f:
            ujson.dump(labeled_dict, f, ensure_ascii=False, indent=2)

        print(f"已儲存 scenario: {scenario}")

    def click_time(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_path = os.path.join(self.data_path, "label_time_recording.txt")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"按下時間：{current_time}\n")

    def save_current_checked(self):
        path = os.path.join(self.data_path, "label_check.txt")
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"{self.ui.comboBox_ego_id.currentText()}\n")


        # make this button to red after clicked
        self.ui.pushButton_check_label_done.setStyleSheet("color: red;")
