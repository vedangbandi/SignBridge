from function import *
from sklearn.model_selection import train_test_split
from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers import LSTM, Dense
from keras.callbacks import TensorBoard, EarlyStopping
import os
import numpy as np

label_map = {label:num for num, label in enumerate(actions)}
print("Loading data from MP_Data...")
print(f"Actions: {actions}")
print(f"Number of sequences per action: {no_sequences}")
print(f"Sequence length: {sequence_length}")

sequences, labels = [], []
for action in actions:
    for sequence in range(no_sequences):
        window = []
        for frame_num in range(sequence_length):
            try:
                res = np.load(os.path.join(DATA_PATH, action, str(sequence), "{}.npy".format(frame_num)), allow_pickle=True)
                window.append(res)
            except Exception as e:
                print(f"Error loading {action}/{sequence}/{frame_num}.npy: {e}")
                # Use zero array if file doesn't exist
                window.append(np.zeros(63))
        sequences.append(window)
        labels.append(label_map[action])

print(f"Total sequences loaded: {len(sequences)}")

# Convert to numpy arrays
X = np.array(sequences)
y = to_categorical(labels).astype(int)

print(f"X shape: {X.shape}")
print(f"y shape: {y.shape}")

# Split data: 75% train, 20% test, 5% validation
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"Training samples: {X_train.shape[0]}")
print(f"Testing samples: {X_test.shape[0]}")

# Setup callbacks
log_dir = os.path.join('Logs')
tb_callback = TensorBoard(log_dir=log_dir)

# Early stopping to prevent overfitting
early_stopping = EarlyStopping(
    monitor='val_categorical_accuracy',
    patience=15,
    restore_best_weights=True,
    verbose=1
)

# Build model
print("\nBuilding LSTM model...")
model = Sequential()
model.add(LSTM(64, return_sequences=True, activation='relu', input_shape=(30, 63)))
model.add(LSTM(128, return_sequences=True, activation='relu'))
model.add(LSTM(64, return_sequences=False, activation='relu'))
model.add(Dense(64, activation='relu'))
model.add(Dense(32, activation='relu'))
model.add(Dense(actions.shape[0], activation='softmax'))

model.compile(optimizer='Adam', loss='categorical_crossentropy', metrics=['categorical_accuracy'])
model.summary()

# Train model
print("\nStarting training...")
history = model.fit(
    X_train, y_train, 
    validation_data=(X_test, y_test),
    epochs=200, 
    callbacks=[tb_callback, early_stopping],
    verbose=1
)

# Evaluate model
print("\nEvaluating model on test set...")
test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)
print(f"Test Loss: {test_loss:.4f}")
print(f"Test Accuracy: {test_accuracy:.4f}")

# Save model
print("\nSaving model...")
model_json = model.to_json()
with open("model.json", "w") as json_file:
    json_file.write(model_json)
model.save('model.h5')
print("Model saved successfully!")