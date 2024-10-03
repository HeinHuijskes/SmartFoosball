from ultralytics import YOLO

# model = YOLO("./yolov8n.yaml")
model = YOLO("./yolov8n.pt")

results = model.train(data="./datasets/complete/data.yaml", epochs=10)