import torch
from torch.utils.data import Dataset
import torchvision.transforms.functional as TF
import torchvision.transforms as transforms
import numpy as np
from PIL import Image

class CelebaShape(Dataset):
    """PyTorch Dataset class for CelebA dataset using labels generated
    from segmentation data

    Parameters
    ----------
    data_folder : str
        Path to folder containing CelebA dataset
    shape_labels : str
        Path to shape labels txt file
    fold : {"train", "val", "test"}, default="train"
        Dataset fold to use.
    use_transforms : bool, default=False
        Whether to augment images with flipping, cropping, and rotation

    Attributes
    ----------
    images : list of str
        List containing path to all images in the dataset
    labels : list of float array
        List containing all labels. Each label vector constists of 25
        floats in the range [0,1] representing a percentile for non-
        binary attributes or a binary value for binary attributes.
    attributes : list of str
        List of attributes
    """
    def __init__(self, data_folder, shape_labels,
                 fold="train", use_transforms=False):
        super().__init__()
        self.images = []
        self.labels = []

        # load images and labels
        with open(shape_labels) as labels_f:
            self.attributes = labels_f.readline().strip("\n").split()
            for line in labels_f:
                line_data = line.rstrip(" \n").split(" ")

                image_n = int(line_data[1][:6])
                labels = np.array([float(d) for d in line_data[2:]])

                train_cond = fold == "train" and image_n < 162771
                val_cond = fold == "val" and image_n>=162771 and image_n<182638
                test_cond = fold == "test" and image_n >= 182638
                if train_cond or val_cond or test_cond:
                    self.images.append(
                        f"{data_folder}/images/{image_n:06d}.jpg")
                    self.labels.append(labels)

        self._use_transforms = use_transforms
        if self._use_transforms:
            self._flip_aug = transforms.RandomHorizontalFlip(p=0.5)
            self._rotation_aug = transforms.RandomRotation(degrees=10)
            self._crop_aug = transforms.RandomCrop((274,224),
                                                   pad_if_needed=True)

    def __getitem__(self, index):
        """Function for obtaining dataset value at provided index.

        Parameters
        ----------
        index : int
            index of item in the dataset

        Returns
        -------
        float tensor
            3x274x224 float tensor representing image.
        float tensor
            25-element float tensor containg labels for the selected
            image.
        """
        image = Image.open(self.images[index])
        label = torch.tensor(self.labels[index])

        if self._use_transforms:
            scale_amount = torch.rand(1).item()*.2+.9
            image = image.resize((int(224*scale_amount),int(274*scale_amount)))
            image = self._crop_aug(image)
            image = self._flip_aug(image)
            image = self._rotation_aug(image)
        else:
            image = image.resize((224,274))

        return TF.to_tensor(image), label

    def __len__(self):
        return len(self.images)

if __name__ == "__main__":
    dataset = CelebaShape("../../CelebA", "shape-labels.txt")
    print("Dataset size:", len(dataset))
    print("Attributes:", dataset.attributes)
    sample_image, sample_label = dataset[0]
    print("Image shape:", sample_image.shape)
    print("Label shape:", sample_label.shape)

    print(sample_label)

    import matplotlib.pyplot as plt
    plt.imshow(np.moveaxis(sample_image.numpy(), 0, -1))
    plt.show()
