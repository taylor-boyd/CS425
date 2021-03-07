import numpy as np
import torch
from shape_predict_train import AttributeNN
import torchvision.transforms.functional as TF
from PIL import Image

class ShapePredictor():
    """Wrapper for AttributeNN network for predicting attributes.

    Parameters
    ----------
    model_path : str
        Path to trained AttributeNN model
    label_path : str
        Path to shape labels file. Needed for collecting attribute
        names.
    device : str, default = "cpu"
        Device to use for predictions. If a GPU is available and a
        version of pytorch which supports GPU training is installed,
        use "cuda".

    Attributes
    ----------
    network : nn.Module
        Trained AttributeNN network
    attributes : list of str
        List of attribute labels
    """
    def __init__(self, model_path, label_path, device="cpu"):
        self.network = AttributeNN(25)
        self.network.requires_grad = False
        self.network.eval()

        self._device = torch.device(device)
        self.network.load_state_dict(torch.load(model_path,
            map_location=self._device))

        with open(label_path) as input_f:
            self.attributes = input_f.readlines()[0].split()

    def process_image(self, input):
        """Function for predicting percentiles / binary features for
        each attribute. Takes a PIL image as input and returns a
        dictionary containing predictions. Non-binary attributes are
        predicted percentiles, binary attributes are probabilities.

        CelebA images have an aspect ratio of 218x178 with the centers
        of the eyes horizontally aligned at a height of 104 pixels with
        40 pixels of horizontal space between them. Input images must
        be aligned in the same way with the same aspect ratio.

        Parameters
        ----------
        input : Image
            Input image as PIL Image object.

        Returns
        -------
        dict
            Dictionary mapping feature names to predicted output in the
            range [0, 1]
        """
        aspect_ratio = input.size[1]/input.size[0]
        if input.size[1] != 274:
            input = input.resize((round(274/aspect_ratio), 274))
        input = TF.to_tensor(TF.center_crop(input, (274, 224))).unsqueeze(0)

        attribute_preds = torch.sigmoid(self.network(input))[0]

        output_dict = {}
        for i, attr in enumerate(self.attributes):
            output_dict[attr] = attribute_preds[i].item()

        return output_dict

if __name__ == "__main__":
    # Simple demo
    import sys
    if len(sys.argv) != 2:
        print("Usage: shape_predict.py IMAGE_FILE")
        exit()

    predictor = ShapePredictor("model/shape_model", "shape-labels.txt")
    test_image = Image.open(sys.argv[1])
    results = predictor.process_image(test_image)
    print(results)
