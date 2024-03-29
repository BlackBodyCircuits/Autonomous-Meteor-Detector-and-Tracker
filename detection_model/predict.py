from ultralytics import YOLO
import os
import random

def run_prediction(imgs: list):
    model = YOLO("runs\\detect\\180epochs_5517\\weights\\best.pt")

    preds = model(imgs)

    for result in preds:
        boxes = result.boxes  # Boxes object for bounding box outputs
        probs = result.probs  # Probs object for classification outputs
        result.show()  # display to screen
        result.save(filename='result.jpg')
        print(boxes, probs)




if __name__ == "__main__":
    n = 15
    images = []
    for root, dirs, files in os.walk("datasets\\CLEAN_DATA_RESIZED\\images\\test"):
        files = random.sample(files, n)
        for file in files:
            images.append(os.path.join(root, file))

    # print(images)
    # imgs = [os.path.join(root, ) for root, dirs, files in "datasets\\CLEAN_DATA\\images\\test": ]
    images = ["C:\\Users\\Jaspe\\ECE_492\\Autonomous-Meteor-Detector-and-Tracker\\camera_obstruction_detection\\test_imgs\\20240309T100422Z.jpg", "datasets\\CLEAN_DATA\\images\\test\\15.jpg"]
    run_prediction(images)