from ultralytics import YOLO

model = YOLO("yolov8n.yaml")
model = YOLO("yolov8n.pt")

results = model.train(data="custom.yaml", epochs=100)