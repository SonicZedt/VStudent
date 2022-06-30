import numpy as np

class RadioButton:
    def __init__(self, image:np.ndarray, threshold:int=200):
        """ Radio button constructor
        params: array, image of radio button
        params: int, threshold an image with more avg white pixel than threshold is considered as selected """
        self.threshold = threshold
        self.image = image

    @property
    def avg(self):
        """ Average pixel value of image """
        return np.average(self.image)

    @property
    def is_selected(self):
        """ Check if the radio button is selected """
        # selected radio button has more white pixel
        return np.sum(self.image >= self.avg) > self.threshold

    @property
    def bright_avg(self):
        """ Birght pixel count of image """
        return np.sum(self.image >= self.avg)

    def brighten_color(self) -> np.ndarray:
        """ Brighten non-black color of image
        return: np.ndarray as new image """
        image = self.image.copy()
        avg = np.average(image)
        image[image > avg] = 255
        image[image <= avg] = 0
        self.image = image