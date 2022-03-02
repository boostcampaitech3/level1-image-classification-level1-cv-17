import argparse
import os
from importlib import import_module

import pandas as pd
import torch
from torch.utils.data import DataLoader

from dataset import TestDataset, MaskBaseDataset

from model import PipeLineModel


# def load_model(saved_model, num_classes, device):
#     model_cls = getattr(import_module("model"), args.model)
#     freeze = args.freeze
#     model = model_cls(
#         num_classes=num_classes
#     )

#     # tarpath = os.path.join(saved_model, 'best.tar.gz')
#     # tar = tarfile.open(tarpath, 'r:gz')
#     # tar.extractall(path=saved_model)

#     model_path = os.path.join(saved_model, 'last.pt')
#     model.load_state_dict(torch.load(model_path, map_location=device))

#     return model


@torch.no_grad()
def inference(data_dir, model_dir, output_dir, args):
    use_cuda = torch.cuda.is_available()
    device = torch.device("cuda" if use_cuda else "cpu")

    model = PipeLineModel(device, args.dtype).to(device)
    model.eval()

    img_root = os.path.join(data_dir, args.data_folder)
    info_path = os.path.join(data_dir, 'output_maskgender.csv')
    info = pd.read_csv(info_path)
    img_paths = [os.path.join(img_root, img_id) for img_id in info.ImageID]

    dataset = TestDataset(img_paths, info['mask'].tolist(), info['gender'].tolist(), mean=(0.548, 0.504, 0.479), std=(0.237, 0.247, 0.246))

    loader = torch.utils.data.DataLoader(
        dataset,
        batch_size=args.batch_size,
        num_workers=8,
        shuffle=False,
        pin_memory=use_cuda,
        drop_last=False,
    )

    print("Calculating inference results..")
    preds = []
    with torch.no_grad():
        for idx, data in enumerate(loader):
            images, mask, gender = data
            images = images.to(device)
            pred = model(images, mask, data)
            preds.append(pred)
    info['ageMod10'] = preds
    info.to_csv(os.path.join(output_dir, args.file_name), index=False)
    print(f'Inference Done!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # Data and model checkpoints directories
    parser.add_argument('--batch_size', type=int, default=1, help='input batch size for validing (default: 1000)')
    parser.add_argument('--data_folder', type=str, default='images')
    parser.add_argument('--dtype', type=str, default='SC')

    # Container environment
    parser.add_argument('--data_dir', type=str, default=os.environ.get('SM_CHANNEL_EVAL', '/opt/ml/input/data/eval'))
    parser.add_argument('--model_dir', type=str, default=os.environ.get('SM_CHANNEL_MODEL', './model'))
    parser.add_argument('--output_dir', type=str, default=os.environ.get('SM_OUTPUT_DATA_DIR', './output'))
    parser.add_argument('--file_name', type=str, default=os.environ.get('SM_OUTPUT_DATA_DIR', './output'))

    args = parser.parse_args()

    data_dir = args.data_dir
    model_dir = args.model_dir
    output_dir = args.output_dir

    os.makedirs(output_dir, exist_ok=True)

    inference(data_dir, model_dir, output_dir, args)
