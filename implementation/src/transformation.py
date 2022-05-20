import numpy as np
import time


class Transformation:
    """ This class is used for defining a `transformation` and applying it to a given `image` """
    def __init__(self, name, func):
        self.name = name
        self.func = func

    def apply(self, image):
        """ Apply the transformation to the given `image`, returning the `transformed_image` """
        if not isinstance(image, np.ndarray):
            raise ValueError('Image must be of type `numpy ndarray`')

        start = time.time()
        print('Applying transformation {:<18}'.format('`' + self.name + '`'), end='', flush=True)
        transformed_image = self.func(image)

        if type(transformed_image) != type(image):
            raise ValueError(f'Type of images differ after transformation `{self.name}`')
        if transformed_image.shape != image.shape:
            raise ValueError(f'Expected output shape:`{image.shape}`, got `{transformed_image.shape}`')

        end = time.time()
        print('[{:.3f} sec]'.format(end - start))
        return transformed_image
