import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models
from functools import reduce
import os

class BaseModel(nn.Module):
    def __init__(self, num_classes):
        super().__init__()

        self.conv1 = nn.Conv2d(3, 32, kernel_size=7, stride=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, stride=1)
        self.dropout1 = nn.Dropout(0.25)
        self.dropout2 = nn.Dropout(0.25)
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(128, num_classes)

    def forward(self, x):
        x = self.conv1(x)
        x = F.relu(x)

        x = self.conv2(x)
        x = F.relu(x)
        x = F.max_pool2d(x, 2)
        x = self.dropout1(x)

        x = self.conv3(x)
        x = F.relu(x)
        x = F.max_pool2d(x, 2)
        x = self.dropout2(x)

        x = self.avgpool(x)
        x = x.view(-1, 128)
        return self.fc(x)


class Resnet18(nn.Module):
    def __init__(self, num_classes, freeze=True):
        super().__init__()

        model = models.resnet18(pretrained=True)
        num_ftrs = model.fc.in_features
        
        if(freeze):
            for n, p in model.named_parameters():
                if 'fc' not in n:
                    p.requires_grad = False

        model.fc = nn.Sequential(
        nn.Dropout(0.5),
        nn.Linear(num_ftrs, 1024),
        nn.Dropout(0.2),
        nn.Linear(1024, 512),
        nn.Dropout(0.1),
        nn.Linear(512, num_classes))

        self.model = model

    def forward(self, x):
        return self.model(x)

class Resnet34(nn.Module):
    def __init__(self, num_classes, freeze=True):
        super().__init__()
        self.resnet34 = models.resnet34(pretrained=True)
        num_ftrs = self.resnet34.fc.in_features
        self.resnet34.fc = nn.Sequential(
        nn.Dropout(0.5),
        nn.Linear(num_ftrs, 1024),
        nn.Dropout(0.2),
        nn.Linear(1024, 512),
        nn.Dropout(0.1),
        nn.Linear(512, num_classes))

    def forward(self, x):
        return self.resnet34(x)



class EfficientB0(nn.Module):
    model_name = 'efficientnet-b0'
    def __init__(self, num_classes, freeze=True):
        super().__init__()

        from efficientnet_pytorch import EfficientNet
        model = EfficientNet.from_pretrained(self.model_name, num_classes=num_classes)
        if(freeze):
            for n, p in model.named_parameters():
                if '_fc' not in n:
                    p.requires_grad = False

        for name, mod in reversed(list(model.named_modules())):
            if isinstance(mod, nn.Linear):
                mod_path = name.split('.')
                classifier_parent = reduce(nn.Module.get_submodule, mod_path[:-1], model)
                setattr(classifier_parent, mod_path[-1], nn.Sequential(
                    nn.Linear(mod.in_features, 4096),
                    nn.ReLU(inplace=True),
                    nn.Dropout(0.7),
                    nn.Linear(4096, 4096),
                    nn.ReLU(inplace=True),
                    nn.Dropout(0.5),
                    nn.Linear(4096, num_classes)
                ))
                break

        self.model = model

    def forward(self, x):
        return self.model(x)

class EfficientB2(EfficientB0):
    model_name = 'efficientnet-b2'
    def __init__(self, num_classes, freeze=True):
        super().__init__(num_classes, freeze=True)

class EfficientB4(EfficientB0):
    model_name = 'efficientnet-b4'
    def __init__(self, num_classes, freeze=True):
        super().__init__(num_classes, freeze=True)

class PipeLineModel(nn.Module):
    def __init__(self, device):
        super().__init__()

        model_path = '/opt/ml/code/model'
        self.mask =  Resnet18(3)
        self.mask.load_state_dict(torch.load(os.path.join(model_path, 'RES18_AUGU_MASK_FC','last.pt'), map_location=device))
        self.mask0_gender =  Resnet18(2)
        self.mask0_gender.load_state_dict(torch.load(os.path.join(model_path, 'RES18_AUGU_MASK0_GENDER_FC','last.pt'), map_location=device))
        self.mask1_gender =  Resnet18(2)
        self.mask1_gender.load_state_dict(torch.load(os.path.join(model_path, 'RES18_AUGU_MASK1_GENDER_FC','last.pt'), map_location=device))
        self.mask2_gender =  Resnet18(2)
        self.mask2_gender.load_state_dict(torch.load(os.path.join(model_path, 'RES18_AUGU_MASK2_GENDER_FC','last.pt'), map_location=device))
        self.mask0_gender0_agemod10 =  Resnet18(7)
        self.mask0_gender0_agemod10.load_state_dict(torch.load(os.path.join(model_path, 'RES18_AUGU_MASK0_GENDER0_AGEMOD10_FC','last.pt'), map_location=device))
        self.mask1_gender0_agemod10 =  Resnet18(7)
        self.mask1_gender0_agemod10.load_state_dict(torch.load(os.path.join(model_path, 'RES18_AUGU_MASK1_GENDER0_AGEMOD10_FC','last.pt'), map_location=device))
        self.mask2_gender0_agemod10 =  Resnet18(7)
        self.mask2_gender0_agemod10.load_state_dict(torch.load(os.path.join(model_path, 'RES18_AUGU_MASK2_GENDER0_AGEMOD10_FC','last.pt'), map_location=device))
        self.mask0_gender1_agemod10 =  Resnet18(7)
        self.mask0_gender1_agemod10.load_state_dict(torch.load(os.path.join(model_path, 'RES18_AUGU_MASK0_GENDER1_AGEMOD10_FC','last.pt'), map_location=device))
        self.mask1_gender1_agemod10 =  Resnet18(7)
        self.mask1_gender1_agemod10.load_state_dict(torch.load(os.path.join(model_path, 'RES18_AUGU_MASK1_GENDER1_AGEMOD10_FC','last.pt'), map_location=device))
        self.mask2_gender1_agemod10 =  Resnet18(7)
        self.mask2_gender1_agemod10.load_state_dict(torch.load(os.path.join(model_path, 'RES18_AUGU_MASK2_GENDER1_AGEMOD10_FC','last.pt'), map_location=device))

    def forward(self, x):
        mask = self.mask(x).argmax(dim=-1).item()
        if(mask == 0):
            gender = self.mask0_gender(x).argmax(dim=-1).item()
            if(gender == 0):
                ageMod10 = self.mask0_gender0_agemod10(x).argmax(dim=-1).item()
                if(ageMod10 == 6):
                    age = 2
                elif(ageMod10 >= 3):
                    age = 1
                else:
                    age = 0
            else:
                ageMod10 = self.mask0_gender1_agemod10(x).argmax(dim=-1).item()
                if(ageMod10 == 6):
                    age = 2
                elif(ageMod10 >= 3):
                    age = 1
                else:
                    age = 0
        elif(mask == 1):
            gender = self.mask1_gender(x).argmax(dim=-1).item()
            if(gender == 0):
                ageMod10 = self.mask1_gender0_agemod10(x).argmax(dim=-1).item()
                if(ageMod10 == 6):
                    age = 2
                elif(ageMod10 >= 3):
                    age = 1
                else:
                    age = 0
            else:
                ageMod10 = self.mask1_gender1_agemod10(x).argmax(dim=-1).item()
                if(ageMod10 == 6):
                    age = 2
                elif(ageMod10 >= 3):
                    age = 1
                else:
                    age = 0
        elif(mask == 2):
            gender = self.mask2_gender(x).argmax(dim=-1).item()
            if(gender == 0):
                ageMod10 = self.mask2_gender0_agemod10(x).argmax(dim=-1).item()
                if(ageMod10 == 6):
                    age = 2
                elif(ageMod10 >= 3):
                    age = 1
                else:
                    age = 0
            else:
                ageMod10 = self.mask2_gender1_agemod10(x).argmax(dim=-1).item()
                if(ageMod10 == 6):
                    age = 2
                elif(ageMod10 >= 3):
                    age = 1
                else:
                    age = 0

        return mask * 6 + gender * 3 + age
    # def __init__(self,num_classes):
    #     super(efficientnetModel,self).__init__()

    #     self.num_classes = num_classes
    #     self.model = torchvision.models.efficientnet_b0(pretrained = True)
        
    #     num_ftrs = self.model.classifier[1].in_features

    #     self.model.fc = nn.Sequential(
    #         nn.Dropout(0.5),
    #         nn.Linear(num_ftrs, 1024),
    #         nn.Dropout(0.2),
    #         nn.Linear(1024, 512),
    #         nn.Dropout(0.1),
    #         nn.Linear(512, self.num_classes)) 
    # self.model.classifier[1] = nn.Sequential(
    #         nn.Dropout(0.5),
    #         nn.Linear(num_ftrs, 1024),
    #         nn.Dropout(0.2),
    #         nn.Linear(1024, 512),
    #         nn.Dropout(0.1),
    #         nn.Linear(512, self.num_classes))
