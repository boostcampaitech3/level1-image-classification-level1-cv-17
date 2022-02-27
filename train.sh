python train.py --epoch 15 --dataset MaskBaseByKindDataset --model EfficientB2 --val_ratio 0.2 --name B2_FaceCrop_MASK --kind mask --data_dir /opt/ml/input/data/train/images_faceCrop
python train.py --epoch 15 --dataset MaskBaseByKindDataset --model EfficientB2 --val_ratio 0.01 --name B2_FaceCrop_MASK_FULLTRAIN --kind mask --data_dir /opt/ml/input/data/train/images_faceCrop
python train.py --epoch 15 --dataset MaskBaseByKindDataset --model EfficientB2 --val_ratio 0.2 --name B2_FaceCrop_GENDER --kind gender --data_dir /opt/ml/input/data/train/images_faceCrop
python train.py --epoch 15 --dataset MaskBaseByKindDataset --model EfficientB2 --val_ratio 0.01 --name B2_FaceCrop_GENDER_FULLTRAIN --kind gender --data_dir /opt/ml/input/data/train/images_faceCrop
python train.py --epoch 15 --dataset MaskBaseByKindDataset --model EfficientB2 --val_ratio 0.2 --name B2_FaceCrop_AGE --kind age --data_dir /opt/ml/input/data/train/images_faceCrop
python train.py --epoch 15 --dataset MaskBaseByKindDataset --model EfficientB2 --val_ratio 0.01 --name B2_FaceCrop_AGE_FULLTRAIN --kind age --data_dir /opt/ml/input/data/train/images_faceCrop