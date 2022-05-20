from transformation import Transformation


class Pipeline:
    """
    This class is used for storing and manipulating a `list` of
    transformations which will be applied to a given image.

    This approach is scalabe and robust, because we can easily
    manipulate whatever transformation we want from the pipeline,
    without needing to create a new list from scratch.
    """
    def __init__(self, name):
        self.name = name
        self.transformations = []

    def add(self, transformation):
        """ Add a transformation in the pipeline """
        if isinstance(transformation, Transformation):
            self.transformations.append(transformation)
        else:
            raise ValueError(
                f'The argument {transformation} of type'
                f'{type(transformation)} is not the type {type(Transformation)}')

    def remove(self, transformation_name):
        """ Remove a transformation from the pipeline, given the `transf_name` """
        for i, transformation in enumerate(self.transformations):
            if transformation.name == transformation_name:
                del self.transformations[i]
                break

    def replace(self, transf_to_replace_name, new_transf):
        """ Replace the transformation with the name `transf_name` with the given `new_transf` """
        if isinstance(new_transf, Transformation):
            for i, curr_transformation in enumerate(self.transformations):
                if curr_transformation.name == transf_to_replace_name:
                    self.transformations[i] = new_transf
                    break
        else:
            raise ValueError(
                f'The argument {new_transf} of type'
                f'{type(new_transf)} is not the type {type(Transformation)}')

    def transform(self, image):
        """ Sequentially apply the transformations from the pipeline to the given `image` """
        for transformation in self.transformations:
            image = transformation.apply(image)
        return image

    def show(self):
        """ Print all the transformations from the pipeline """
        for idx, transformation in enumerate(self.transformations):
            print(f'{idx + 1}: {transformation.name}')
