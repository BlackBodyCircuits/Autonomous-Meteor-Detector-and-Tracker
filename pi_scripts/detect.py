import cv2
import numpy as np
import os

def perfrom_dilataion(img, size=2, shape=cv2.MORPH_RECT):
    '''
        Perfrom dilation on an image
    '''
    dilation_shape = shape
    dilatation_size = size
    # set the kernal to be used during dilation
    element = cv2.getStructuringElement(dilation_shape, (2 * dilatation_size + 1, 2 * dilatation_size + 1),(dilatation_size, dilatation_size))
    # perform and return the result of the image dilation
    return cv2.dilate(img, element)

def get_edges(img, detection_type="canny"):
    '''
        Perfrom the specified edge detection operation on the image\n
        By default this will be canny edge detection
    '''
    if detection_type == "canny":
        # Setting parameter values 
        t_lower = 25  # Lower Threshold 
        t_upper = 150  # Upper threshold 

        edge = cv2.Canny(img, t_lower, t_upper) 

    elif detection_type == "sobel":
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        scale = 1
        delta = 0
        ddepth = cv2.CV_16S
        grad_x = cv2.Sobel(gray, ddepth, 1, 0, ksize=3, scale=scale, delta=delta, borderType=cv2.BORDER_DEFAULT)
        # Gradient-Y
        grad_y = cv2.Sobel(gray, ddepth, 0, 1, ksize=3, scale=scale, delta=delta, borderType=cv2.BORDER_DEFAULT)

        abs_grad_x = cv2.convertScaleAbs(grad_x)
        abs_grad_y = cv2.convertScaleAbs(grad_y)

        edge = cv2.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)
    else:
        return img
    
    return edge

def detect_obstruction(img, verbose=False):
    '''
        Given an image taken by a camera, detect if there is something obstructing the view
    '''
    image_size = 200
    img = cv2.resize(img, (image_size, image_size))
    img = cv2.GaussianBlur(img, [21, 21], 1)

    
    # Applying the Canny Edge filter 
    edge = get_edges(img)

    # dilate the binary image
    edge = perfrom_dilataion(edge) 

    # get all the contours of the binary image
    contours, hierarchy = cv2.findContours(edge, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) 

    # if no contours were detected we cannot make any conclusions
    if len(contours) == 0:
        return False

    c = max(contours, key = cv2.contourArea)

    # get the area taken up by the contours
    tot_area = sum(cv2.contourArea(contour) for contour in contours)
    max_area = cv2.contourArea(c)
    max_p = max_area / image_size**2
    tot_p = tot_area / image_size**2
    
    
    if verbose:
        print(f"Max Contour area: {max_area}, Total contour area: {tot_area}")
        print(f"Max Contour percent: {max_p * 100:.1f}%, Total contour percent: {tot_p * 100:.1f}%")

        cv2.drawContours(img, contours, -1, (0, 125, 0), 3) 
        cv2.drawContours(img, [c], -1, (0, 0, 255), 3) 

        cv2.imshow('Contours', img)
        cv2.imshow('original', img) 
        cv2.imshow('edge', edge) 
        cv2.waitKey(0) 
        cv2.destroyAllWindows() 

    return tot_p > 0.20


if __name__ == "__main__":
    path_local_images = os.path.join("/home/raspberrypi/Desktop/images")
    for filename in os.listdir(path_local_images):
        print(filename)
        img = cv2.imread(os.path.join(path_local_images, filename))
        print(detect_obstruction(img, True))
        
