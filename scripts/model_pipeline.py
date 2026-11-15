#%%
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from sklearn.model_selection import GroupShuffleSplit


#%% récupération des données:
X = np.load("../data/features/X.npy")
labels = np.load("../data/features/labels.npy")
coureurs = np.load("../data/features/coureurs.npy")

set_labels, y = np.unique(labels, return_inverse=True)# on encode les classes

print("X :", X.shape)
print("y :", y.shape)
print(set_labels)

#%% séparation des données d'entrainement/test/valisation

# 70 % train, 30 % temporaire (validation + test)
split1 = GroupShuffleSplit(n_splits=1, test_size=0.30, random_state=42)
train_idx, temp_idx = next(split1.split(X, y, groups=coureurs)) # on sépare mais on garde les foulées des coureurs groupés

# 15 % validation, 15 % test
split2 = GroupShuffleSplit(n_splits=1, test_size=0.50, random_state=42)
val_rel_idx, test_rel_idx = next(split2.split(X[temp_idx], y[temp_idx], groups=coureurs[temp_idx]))

val_idx = temp_idx[val_rel_idx]
test_idx = temp_idx[test_rel_idx]


#%%

# Conversion en tenseurs
X_tensor = torch.tensor(X, dtype=torch.float32)
y_tensor = torch.tensor(y, dtype=torch.long)

del X #on supprime l'objet pour libérer de la mémoire
del y

# Datasets
train_dataset = TensorDataset(X_tensor[train_idx], y_tensor[train_idx])
val_dataset = TensorDataset(X_tensor[val_idx], y_tensor[val_idx])
test_dataset = TensorDataset(X_tensor[test_idx], y_tensor[test_idx])

# DataLoaders
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)
test_loader = DataLoader(test_dataset,batch_size=32, shuffle=False)


#%%

class CNNFoulee(nn.Module):

    def __init__(self, nb_classes):
        super().__init__()

        self.features = nn.Sequential(
            nn.Conv1d(84, 64, kernel_size=7, padding=3),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.MaxPool1d(2),

            nn.Conv1d(64, 128, kernel_size=5, padding=2),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.MaxPool1d(2),

            nn.Conv1d(128, 128, kernel_size=3, padding=1),
            nn.BatchNorm1d(128),
            nn.ReLU(),

            nn.AdaptiveAvgPool1d(1)
        )

        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, nb_classes)
        )

    def forward(self, x):
        x = self.features(x)
        return self.classifier(x)


model = CNNFoulee(nb_classes=3)

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(),lr=0.001)


for X_batch, y_batch in train_loader:

    optimizer.zero_grad()

    predictions = model(X_batch)

    loss = criterion(predictions, y_batch)

    loss.backward()
    optimizer.step()
# %%
