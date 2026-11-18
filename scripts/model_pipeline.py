#%%
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from sklearn.model_selection import GroupShuffleSplit
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import confusion_matrix, classification_report
import matplotlib.pyplot as plt
from charte_graphique import appliquer_charte, COULEURS_GROUPES, titrer, sauver_figure
from pathlib import Path

#%%

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Appareil utilisé :", device)

if device.type == "cuda":
    print(torch.cuda.get_device_name(0))

appliquer_charte()


#%% récupération des données et analyse:

BASE_DIR = Path(__file__).resolve().parent

X = np.load(BASE_DIR.parent/"data/features/foulee.npy")
labels = np.load(BASE_DIR.parent/"data/features/label_foulee.npy")
coureurs = np.load(BASE_DIR.parent/"data/features/coureur_foulee.npy")


# Quelques percentiles pour examiner la distribution
print("percentiles des features : ", np.percentile(X,[0, 1, 5, 25, 50, 75, 95, 99, 100]))


set_labels, y, counts = np.unique(labels, return_inverse=True, return_counts = True)# on encode les classes

print("X :", X.shape)
print("y :", y.shape)
print(set_labels)
for classe, count in zip(set_labels, counts):
    print(classe, count, f"({100 * count / len(labels):.1f} %)")



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


# Calcul sur les foulées d'entraînement uniquement
X_train = X_tensor[train_idx]

mean = X_train.mean(dim=(0, 2), keepdim=True)
std = X_train.std(dim=(0, 2), keepdim=True)

# Éviter une division par zéro
std = torch.clamp(std, min=1e-6)

# Standardisation de toutes les données
X_tensor = (X_tensor - mean) / std

del X_train


classes = np.unique(y[train_idx])

weights = compute_class_weight(
    class_weight="balanced",
    classes=classes,
    y=y[train_idx])

weights = torch.tensor(weights, dtype=torch.float32).to(device)

print("Poids des classes :", weights)

print("Train :", np.unique(y[train_idx], return_counts=True))
print("Val :", np.unique(y[val_idx], return_counts=True))
print("Test :", np.unique(y[test_idx], return_counts=True))

print("Min :", X_tensor.min().item())
print("Max :", X_tensor.max().item())
print("Moyenne :", X_tensor.mean().item())
print("Écart-type :", X_tensor.std().item())

print("NaN :", torch.isnan(X_tensor).any().item())
print("Inf :", torch.isinf(X_tensor).any().item())

del X #on supprime l'objet pour libérer de la mémoire
del y

# Datasets
train_dataset = TensorDataset(X_tensor [train_idx], y_tensor[train_idx])
val_dataset = TensorDataset(X_tensor[val_idx], y_tensor[val_idx])
test_dataset = TensorDataset(X_tensor[test_idx], y_tensor[test_idx])

# DataLoaders
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, pin_memory=(device.type == "cuda"))
val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False, pin_memory=(device.type == "cuda"))
test_loader = DataLoader(test_dataset,batch_size=32, shuffle=False, pin_memory=(device.type == "cuda"))

#%% définition du model

class CNNFoulee_initial(nn.Module):

    def __init__(self, nb_classes):
        super().__init__()

        self.layers = nn.Sequential(
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
            nn.Dropout(0.4),
            nn.Linear(64, nb_classes)
        )

    def forward(self, x):
        out = self.layers(x)
        return self.classifier(out)

#%%

class CNNFoulee_compact(nn.Module):

    def __init__(self, nb_classes):
        super().__init__()

        self.layers = nn.Sequential(
            nn.Conv1d(84, 32, kernel_size=7, padding=3),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.MaxPool1d(2),

            nn.Conv1d(32, 64, kernel_size=5, padding=2),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.MaxPool1d(2),

            nn.Conv1d(64, 64, kernel_size=3, padding=1),
            nn.BatchNorm1d(64),
            nn.ReLU(),

            nn.AdaptiveAvgPool1d(1)
        )

        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(64, nb_classes)
        )

    def forward(self, x):
        out = self.layers(x)
        return self.classifier(out)


#%% boucles d'entrainement et de test:

def train_loop(dataloader, model, loss_fn, optimizer):
    model.train()
    total_loss = 0
    for X, y in dataloader:

        X = X.to(device, non_blocking=True)
        y = y.to(device, non_blocking=True)

        optimizer.zero_grad()
        pred = model(X) #forward pass
        loss = loss_fn(pred, y)

        # Backpropagation
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
    return total_loss / len(dataloader)   # loss moyenne (comparable à la validation)

def test_loop(dataloader, model, loss_fn):
    model.eval()
    size = len(dataloader.dataset)
    num_batches = len(dataloader)
    test_loss, correct = 0, 0

    with torch.no_grad():
        for X, y in dataloader:
            X = X.to(device, non_blocking=True)
            y = y.to(device, non_blocking=True)

            pred = model(X)
            test_loss += loss_fn(pred, y).item()
            correct += (pred.argmax(1) == y).sum().item()

    test_loss /= num_batches
    correct /= size

    return test_loss, 100 * correct


def evaluate_model(dataloader, model):
    model.eval()
    y_true = []
    y_pred = []

    with torch.no_grad():
        for X, y in dataloader:
            X = X.to(device)
            pred = model(X)

            y_true.extend(y.numpy())
            y_pred.extend(pred.argmax(1).cpu().numpy())

    print(classification_report(y_true,y_pred,target_names=set_labels))
    print(confusion_matrix(y_true, y_pred))


#%%

epochs = 1000
loss_test = []
loss_train = []
acc_test = []
acc_train = []
if 'model' in locals():
    del model
if 'loss_fn' in locals():
    del loss_fn
if 'optimizer' in locals():
    del optimizer


model = CNNFoulee_compact(nb_classes=3).to(device)
loss_fn = nn.CrossEntropyLoss(weight=weights)
optimizer = torch.optim.Adam(
    model.parameters(),
    lr=0.0001,
    weight_decay=1e-4)


meilleur_val_loss = float("inf")
patience = 20
epochs_sans_amelioration = 0

for t in range(epochs):

    l_train = train_loop(train_loader, model, loss_fn, optimizer)
    _, at = test_loop(train_loader, model, loss_fn)
    l_val, a_val = test_loop(val_loader, model, loss_fn)

    loss_train.append(l_train)
    loss_test.append(l_val)
    acc_train.append(at)
    acc_test.append(a_val)

    print(
        f"Epoch {t+1} | "
        f"Train loss: {l_train:.4f} | "
        f"Val loss: {l_val:.4f} | "
        f"Train acc: {at:.2f}% | "
        f"Val acc: {a_val:.2f}%"
    )

    if l_val < meilleur_val_loss:
        meilleur_val_loss = l_val
        epochs_sans_amelioration = 0
    else:
        epochs_sans_amelioration += 1

    if epochs_sans_amelioration >= patience:
        print("Early stopping !")
        break

print("Done!")


# %% visualisation de la loss et de l'accuracy

evaluate_model(test_loader, model)

fig, (ax1, ax2) = plt.subplots(2,1)
ax1.plot(loss_train, label="training")
ax1.plot(loss_test, label="validation")
ax1.set_title("Evolution de la loss au cours des epochs")
ax1.set_ylabel("loss")
ax1.legend()

ax2.plot(acc_train, label="training")
ax2.plot(acc_test, label="validation")
ax2.set_title("Evolution de l'accuracy au cours des epochs")
ax2.set_xlabel("epochs")
ax2.set_ylabel("accuracy (%)")
ax2.legend()

fig.tight_layout()
plt.show()
sauver_figure(fig, "lre-4_compact")
print(f"la performance à la dernière itération est : {acc_test[-1]:.2f} %")

# %%
