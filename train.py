
from pytorch_lightning import Trainer
from pytorch_lightning.callbacks.early_stopping import EarlyStopping
import os
from models import VAE

import argparse
import yaml

def load_config(path="config.yaml"):
    config = yaml.load(open(path),yaml.SafeLoader)
    return config["training_params"],config["model_params"]


if __name__ == "__main__":
    training_params,model_params = load_config()

    model =  VAE(**model_params)
    print("==== Model Architecture ====")
    print(model)
    trainer = Trainer(**training_params)
    trainer.fit(model)
    