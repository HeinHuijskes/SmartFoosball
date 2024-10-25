from ultralytics import YOLO

model = YOLO("./yolov8n.yaml")
model = YOLO("./yolov8n.pt")
# model = YOLO("yolo11n.yaml").load("yolo11n.pt")
# model = YOLO("C:\\Users\\melle\\PycharmProjects\\SmartFoosball\\yolo11n.pt")

if __name__ == '__main__':
    results = model.train(data="./datasets/new_model_datasets/v1_v8/data.yaml", epochs=10, imgsz=640, device=0)
