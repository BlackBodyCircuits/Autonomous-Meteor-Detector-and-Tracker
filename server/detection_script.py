import os
from ultralytics import YOLO
import shutil
import time


def run_prediction(imgs: dict):
    '''
        Run infrence on the new images and add\n
        the positive detections to `server_detections`
    '''
    model_file = os.path.join("model", "best.pt")
    model = YOLO(model_file)

    # print(imgs)
    files = list(imgs.keys())

    # preds = model.predict(files, show=True, save=True, imgsz=640, conf=0.5, max_det=1)

    preds = model(files)

    for i in range(len(preds)):
        result = preds[i]
        # result.show() 
        boxes = result.boxes  # Boxes object for bounding box outputs
        if len(boxes.conf):
            fname = imgs[files[i]]
            # print(fname)
            result.save(filename=os.path.join("server_detections", fname))

def check_for_new_imgs(seen_imgs: set):

    new_imgs = {}
    for root, dirs, files in os.walk("server_imgs"):
        for img in files:
            if not img in seen_imgs:
                # print(img)
                seen_imgs.add(img)
                new_imgs[os.path.join(root, img)] = img
    # print(new_imgs)
    if len(new_imgs) > 0:
        run_prediction(new_imgs)


def init_detection():
    '''
        Runs once to set up the list of existing images 
    '''
    seen = set()
    for (dirpath, dirnames, filenames) in os.walk("server_imgs"):
        seen = set(filenames)
        break
    # seen.remove("pearl3.jpg")
    # seen.remove("pearl2.jpg")
    # print(seen)
    return seen

if __name__ == "__main__":
    seen_imgs = init_detection()
    while True:
        time.sleep(1)
        check_for_new_imgs(seen_imgs)


