import numpy as np
import pandas as pd
import os, json, pickle
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import KFold
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import confusion_matrix, classification_report
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Conv1D, GRU, Dropout, BatchNormalization, Input, Bidirectional
from tensorflow.keras.utils import to_categorical, Sequence
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras import regularizers
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from core.settings import settings

# ==================== PATHS ====================
SCALER_PATH = os.path.join(settings.RESULTS_DIR, 'scaler.pkl')
ENCODER_PATH = os.path.join(settings.RESULTS_DIR, 'label_encoder.pkl')
MODEL_PATH_TEMPLATE = os.path.join(settings.MODEL_DIR, 'gesture_model_fold{}.h5')
METRICS_PATH = settings.METRICS_PATH
RESULTS_DIR = settings.RESULTS_DIR
RAW_DATA_PATH = settings.RAW_DATA_PATH
os.makedirs(RESULTS_DIR, exist_ok=True)

TIMESTEPS = 50
KFOLD_SPLITS = 5
EPOCHS = 20
BATCH_SIZE = 32

# ==================== AUGMENTATION CONFIG ====================
def get_augmentation_config(dataset_size):
    if dataset_size <= 20000:
        config = {
            "time_warp": {"enabled": True, "prob": 0.1},
            "window_slice": {"enabled": True, "prob": 0.7, "max_slices": 2},
            "jitter": {"enabled": True, "prob": 0.3, "noise_level": 0.01},
            "scaling": {"enabled": True, "prob": 0.3},
            "permutation": {"enabled": True, "prob": 0.2}
        }
        mixup_ratio = 0.3
    else:
        config = {
            "time_warp": {"enabled": True, "prob": 0.05},
            "window_slice": {"enabled": True, "prob": 0.5, "max_slices": 1},
            "jitter": {"enabled": True, "prob": 0.2, "noise_level": 0.005},
            "scaling": {"enabled": True, "prob": 0.2},
            "permutation": {"enabled": False}
        }
        mixup_ratio = 0.1
    return config, mixup_ratio

# ==================== LOAD & NORMALIZE DATA ====================
df = pd.read_csv(RAW_DATA_PATH)
if 'session_id' in df.columns:
    df = df.drop('session_id', axis=1)

X_raw = df.drop('label', axis=1).values
y = df['label'].values
NUM_FEATURES = X_raw.shape[1]

scaler = StandardScaler()
X_raw = scaler.fit_transform(X_raw)
with open(SCALER_PATH, "wb") as f:
    pickle.dump(scaler, f)

# ==================== LABEL ENCODING ====================
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)
num_classes = len(np.unique(y_encoded))
with open(ENCODER_PATH, "wb") as f:
    pickle.dump(label_encoder, f)

# ==================== SEQUENCE BUILDING ====================
def build_sequences(X, y, timesteps):
    X_seq, y_seq = [], []
    for i in range(len(X) - timesteps + 1):
        X_seq.append(X[i:i+timesteps])
        y_seq.append(y[i+timesteps-1])
    return np.array(X_seq), np.array(y_seq)

X_seq, y_seq = build_sequences(X_raw, y_encoded, TIMESTEPS)
y_seq_cat = to_categorical(y_seq, num_classes=num_classes)
DATASET_SIZE = len(X_seq)

# ==================== AUGMENTATION CONFIG ====================
AUGMENTATION_CONFIG, MIXUP_RATIO = get_augmentation_config(DATASET_SIZE)
print(f"Dataset size: {DATASET_SIZE}, Aug config: {AUGMENTATION_CONFIG}, Mixup: {MIXUP_RATIO}")

# ==================== DATA GENERATOR ====================
class GestureDataGenerator(Sequence):
    def __init__(self, X, y, batch_size=32, shuffle=True, aug_config=None, mixup_ratio=0.0):
        self.X = X
        self.y = y
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.aug_config = aug_config or {}
        self.mixup_ratio = mixup_ratio
        self.indexes = np.arange(len(self.X))
        self.on_epoch_end()

    def __len__(self):
        return int(np.ceil(len(self.X) / self.batch_size))

    def on_epoch_end(self):
        if self.shuffle:
            np.random.shuffle(self.indexes)

    def __getitem__(self, idx):
        batch_indexes = self.indexes[idx*self.batch_size:(idx+1)*self.batch_size]
        X_batch = self.X[batch_indexes].copy()
        y_batch = self.y[batch_indexes].copy()

        # ---------------- AUGMENTATION ----------------
        for i in range(len(X_batch)):
            x_copy = X_batch[i]
            if self.aug_config.get("time_warp", {}).get("enabled") and np.random.rand() < self.aug_config["time_warp"]["prob"]:
                factor = np.random.uniform(0.8, 1.2)
                idxs = np.round(np.linspace(0, len(x_copy)-1, int(len(x_copy)*factor))).astype(int)
                idxs = np.clip(idxs, 0, len(x_copy)-1)
                x_copy = x_copy[idxs]
                if len(x_copy) < len(X_batch[i]):
                    pad_len = len(X_batch[i]) - len(x_copy)
                    x_copy = np.pad(x_copy, ((0,pad_len),(0,0)), mode='edge')
                else:
                    x_copy = x_copy[:len(X_batch[i])]
            if self.aug_config.get("window_slice", {}).get("enabled") and np.random.rand() < self.aug_config["window_slice"]["prob"]:
                num_slices = np.random.randint(1, self.aug_config["window_slice"]["max_slices"]+1)
                step = len(x_copy)//(num_slices+1)
                start = np.random.randint(0, step)
                x_copy = x_copy[start:start+step*num_slices]
                if len(x_copy) < len(X_batch[i]):
                    pad_len = len(X_batch[i]) - len(x_copy)
                    x_copy = np.pad(x_copy, ((0,pad_len),(0,0)), mode='edge')
                else:
                    x_copy = x_copy[:len(X_batch[i])]
            if self.aug_config.get("jitter", {}).get("enabled") and np.random.rand() < self.aug_config["jitter"]["prob"]:
                x_copy += np.random.normal(0, self.aug_config["jitter"]["noise_level"], x_copy.shape)
            if self.aug_config.get("scaling", {}).get("enabled") and np.random.rand() < self.aug_config["scaling"]["prob"]:
                scale = np.random.uniform(0.9, 1.1)
                x_copy *= scale
            if self.aug_config.get("permutation", {}).get("enabled") and np.random.rand() < self.aug_config["permutation"]["prob"]:
                x_copy = np.random.permutation(x_copy)
            X_batch[i] = x_copy

        # ---------------- MIXUP ----------------
        n_mix = int(len(X_batch) * self.mixup_ratio)
        for _ in range(n_mix):
            i, j = np.random.choice(len(X_batch), 2, replace=False)
            lam = np.random.beta(0.2, 0.2)
            X_batch[i] = lam * X_batch[i] + (1-lam) * X_batch[j]
            y_batch[i] = lam * y_batch[i] + (1-lam) * y_batch[j]

        return X_batch, y_batch

# ==================== MODEL DEFINITION ====================
def build_cnn_bigru(num_classes, use_l2=True, l2_factor=1e-4):
    reg = regularizers.l2(l2_factor) if use_l2 else None
    model = Sequential([
        Input(shape=(TIMESTEPS, NUM_FEATURES)),
        Conv1D(64, 3, activation='relu', padding='same', kernel_regularizer=reg),
        BatchNormalization(),
        Dropout(0.3),
        Bidirectional(GRU(64, return_sequences=True, kernel_regularizer=reg,
                          dropout=0.3, recurrent_dropout=0.3)),
        Bidirectional(GRU(32, return_sequences=False, kernel_regularizer=reg,
                          dropout=0.3, recurrent_dropout=0.3)),
        Dense(64, activation='relu', kernel_regularizer=reg),
        Dropout(0.4),
        Dense(num_classes, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

callbacks = [
    EarlyStopping(patience=15, restore_best_weights=True),
    ReduceLROnPlateau(factor=0.5, patience=5)
]

# ==================== VISUALIZATION ====================
def plot_metrics(history, fold_num):
    # Accuracy
    plt.figure(figsize=(10,6))
    plt.plot(history.history['accuracy'], label='Training Acc')
    plt.plot(history.history['val_accuracy'], label='Validation Acc')
    plt.title(f'Fold {fold_num} Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, f'accuracy_fold{fold_num}.png'))
    plt.close()

    # Loss
    plt.figure(figsize=(10,6))
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title(f'Fold {fold_num} Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, f'loss_fold{fold_num}.png'))
    plt.close()

def plot_confusion_matrix(y_true, y_pred, fold_num):
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(10,8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=label_encoder.classes_,
                yticklabels=label_encoder.classes_)
    plt.title(f'Confusion Matrix Fold {fold_num}')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, f'confusion_matrix_fold{fold_num}.png'))
    plt.close()

# ==================== K-FOLD TRAINING + VISUALIZATION ====================
fold_results = []
kf = KFold(n_splits=KFOLD_SPLITS, shuffle=True, random_state=42)

for fold, (train_idx, val_idx) in enumerate(kf.split(X_seq)):
    print(f"\n===== Fold {fold+1}/{KFOLD_SPLITS} =====")
    X_train_fold, X_val_fold = X_seq[train_idx], X_seq[val_idx]
    y_train_fold, y_val_fold = y_seq_cat[train_idx], y_seq_cat[val_idx]

    train_gen = GestureDataGenerator(X_train_fold, y_train_fold,
                                     batch_size=BATCH_SIZE,
                                     aug_config=AUGMENTATION_CONFIG,
                                     mixup_ratio=MIXUP_RATIO)
    val_gen = GestureDataGenerator(X_val_fold, y_val_fold,
                                   batch_size=BATCH_SIZE,
                                   shuffle=False)

    model = build_cnn_bigru(num_classes)
    history = model.fit(train_gen,
                        validation_data=val_gen,
                        epochs=EPOCHS,
                        callbacks=callbacks,
                        verbose=1)

    # Evaluate & save fold results
    y_val_pred_proba = model.predict(val_gen)
    y_val_pred_classes = np.argmax(y_val_pred_proba, axis=1)
    y_val_true_classes = np.argmax(y_val_fold, axis=1)

    acc = np.mean(y_val_pred_classes == y_val_true_classes)
    print(f"Fold {fold+1} Accuracy: {acc:.3f}")
    fold_results.append(acc)

    # Save fold model
    model.save(MODEL_PATH_TEMPLATE.format(fold+1))

    # Visualization
    plot_metrics(history, fold+1)
    plot_confusion_matrix(y_val_true_classes, y_val_pred_classes, fold+1)

# ==================== RESULTS ====================
avg_acc = np.mean(fold_results)
print(f"\n Average K-Fold Accuracy: {avg_acc:.3f}")

metrics_data = {
    "average_accuracy": float(avg_acc),
    "fold_accuracies": [float(x) for x in fold_results]
}

with open(METRICS_PATH, 'w') as f:
    json.dump(metrics_data, f, indent=2)

print(f"Models, metrics & visualizations saved in {RESULTS_DIR}")
