import os
import cv2

for root, dir, files in os.walk("test_imgs"):
        for file in files:
                path = os.path.join(root, file)
                img = cv2.imread(path)
                img = cv2.resize(img, [1080, 1080])
                cv2.imwrite(path, img)
                

