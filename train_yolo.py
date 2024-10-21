from ultralytics import YOLO

# model = YOLO("./yolov8n.yaml")
# model = YOLO("./yolov8n.pt")
model = YOLO("C:\\Users\\melle\\PycharmProjects\\SmartFoosball\\yolo11n.pt")

if __name__ == '__main__':
    results = model.train(data="./datasets/complete_v11/data.yaml", epochs=10)
