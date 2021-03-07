import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import torchvision.models as models
from torch.optim.lr_scheduler import ReduceLROnPlateau
from celeba import CelebaShape
import time
from pathlib import Path

BATCH_SIZE = 256
LEARNING_RATE = .1
DEVICE = torch.device("cuda:0")

class AttributeNN(nn.Module):
    """Base network for predicting shape labels. Uses a Resnet-18
    backbone.

    Parameters
    ----------
    n_labels : int
        Number of attributes to predict.
    pretrain : bool, default=False
        If true, backbone network will be initialized with weights
        trained on ImageNet.

    Attributes
    ----------
    backbone : nn.Module
        Backbone resnet network
    n_labels : int
        Number of output neurons.
    """
    def __init__(self, n_labels, pretrain=False):
        super().__init__()
        self.backbone = models.resnet18(pretrained=pretrain)
        fc_in_feats = self.backbone.fc.in_features

        self.backbone.fc = nn.Linear(fc_in_feats, n_labels, bias=True)
        self.n_labels = n_labels

    def forward(self, input):
        output = self.backbone(input)
        return output

def train(network, bs, lr, epochs, device):
    """Function for training network on CelebA dataset with shape
    labels. Uses adam optimizer with MSE loss to predict percentiles
    for each attribute. Saves model to model/shape_model.

    Parameters
    ----------
    network : nn.Module
        Neural network to train.
    bs : int
        Batch size.
    lr : int
        Learning rate
    epochs : int
        Number of epochs to train.
    device : torch.device
        Device to train on.
    """
    dataset = CelebaShape("../../CelebA", "shape-labels.txt", fold="train",
                          use_transforms=True)
    dataloader = DataLoader(dataset,batch_size=bs,num_workers=8,shuffle=True)

    dataset_val = CelebaShape("../../CelebA", "shape-labels.txt", fold="val",
                              use_transforms=False)
    dataloader_val = DataLoader(dataset_val, batch_size=bs,
                                num_workers=8, shuffle=True)

    optimizer = optim.Adam(network.parameters())
    loss_function = nn.MSELoss()
    scheduler = ReduceLROnPlateau(optimizer, patience=10, verbose=True)

    Path("model/").mkdir(exist_ok=True)

    print_iter = 150
    start_time = time.time()
    for epoch in range(epochs):
        print(f"EPOCH {epoch}")
        avg_loss = 0
        for i, (batch, labels) in enumerate(dataloader):
            batch = batch.to(device)
            labels = labels.float().to(device)

            network.zero_grad()
            output = torch.sigmoid(network.forward(batch))
            loss = loss_function(output, labels)

            loss.backward()
            avg_loss += loss.item()
            optimizer.step()

            if i % print_iter == 0 and i != 0:
                print(f"{i/len(dataloader)*100:6.2f}% - "
                      f"{avg_loss/print_iter:.4f} - "
                      f"{time.time() - start_time:0.0f}s")
                avg_loss = 0

                torch.save(network.state_dict(), f"model/shape_model")
        torch.save(network.state_dict(), f"model/shape_model")

        with torch.no_grad():
            network.eval()
            avg_loss = 0
            avg_dist = 0
            for batch, labels in dataloader_val:
                batch = batch.to(device)
                labels = labels.float().to(device)

                output = torch.sigmoid(network.forward(batch))
                loss = loss_function(output, labels)

                avg_dist += torch.mean(torch.abs(output - labels)).item()
                avg_loss += loss.item()

            print("Val loss:", avg_loss/len(dataloader_val))
            print("    dist:", avg_dist/len(dataloader_val))
            scheduler.step(avg_loss)
            network.train()

def count_parameters(model):
    """Prints the number of parameters in an nn.Module"""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)

if __name__ == "__main__":
    network = AttributeNN(25, pretrain=True)
    print(count_parameters(network), "parameters")

    network.to(DEVICE)
    train(network, BATCH_SIZE, LEARNING_RATE, 30, DEVICE)
