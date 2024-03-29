from ultralytics import YOLO
import os
import random
import cv2

def run_prediction(imgs: list):

    model = YOLO("model\\best.pt")

    # preds = model.predict(imgs, show=True, save=True, imgsz=640, conf=1, max_det=1)



    preds = model(imgs)

    for i in range(len(preds)):
        result = preds[i]
        boxes = result.boxes  # Boxes object for bounding box outputs
        probs = result.probs  # Probs object for classification outputs
        result.show()  # display to screen
        result.save(filename=f'results/{i}.jpg')
        print(boxes, len(boxes.conf))




if __name__ == "__main__":
    n = 15
    images = []
    for root, dirs, files in os.walk("..\camera_obstruction_detection\\test_imgs"):
        if len(files) > n:
            files = random.sample(files, n)

        for file in files:
            images.append(os.path.join(root, file))

    print(f"Running infrence on {len(images)} images...")

    # print(images)
    # imgs = [os.path.join(root, ) for root, dirs, files in "datasets\\CLEAN_DATA\\images\\test": ]
    # images = ["C:\\Users\\Jaspe\\ECE_492\\Autonomous-Meteor-Detector-and-Tracker\\camera_obstruction_detection\\test_imgs\\20240309T100422Z.jpg", "datasets\\CLEAN_DATA\\images\\test\\15.jpg"]
    run_prediction(images)