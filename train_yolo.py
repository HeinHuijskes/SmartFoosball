from ultralytics import YOLO

# model = YOLO("./yolov8n.yaml")
# model = YOLO("./yolov8n.pt")
model = YOLO("./runs/detect/LaserFog15/weights/best.pt")

if __name__ == '__main__':
    # results = model.train(data="./datasets/laserfog/data.yaml", epochs=10, amp=False, half=False, device=0)
    model.val()
