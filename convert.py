import pickle

print("Loading High-Accuracy CatBoost model...")
with open("high_accuracy_flood_model.pkl", "rb") as f:
    model = pickle.load(f)

print("Exporting to ONNX Edge format...")
model.save_model("model.onnx", format="onnx")

print("✅ Success! 'model.onnx' has been created.")