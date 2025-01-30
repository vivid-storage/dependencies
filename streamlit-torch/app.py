import streamlit as st
import torch
import torch.nn as nn
import torch.optim as optim

# Define a simple linear regression model
class LinearRegressionModel(nn.Module):
    def __init__(self):
        super(LinearRegressionModel, self).__init__()
        self.linear = nn.Linear(1, 1)  # Input and output are both 1-dimensional

    def forward(self, x):
        return self.linear(x)

# Initialize the model, loss function, and optimizer
model = LinearRegressionModel()
criterion = nn.MSELoss()
optimizer = optim.SGD(model.parameters(), lr=0.01)

# Streamlit UI
st.title("Simple PyTorch Linear Regression")

# Input section
st.header("Train the Model")
st.write("Enter training data:")

# Collect user input for training data
x_train = st.text_area("Input X values (comma-separated)", "1, 2, 3, 4")
y_train = st.text_area("Input Y values (comma-separated)", "2, 4, 6, 8")

# Parse the input data
try:
    x_train = torch.tensor([[float(x)] for x in x_train.split(",")], dtype=torch.float32)
    y_train = torch.tensor([[float(y)] for y in y_train.split(",")], dtype=torch.float32)
except ValueError:
    st.error("Invalid input! Please enter numbers separated by commas.")
    st.stop()

if st.button("Train Model"):
    # Train the model for a few epochs
    st.write("Training the model...")
    for epoch in range(100):  # Simple fixed number of epochs
        optimizer.zero_grad()
        outputs = model(x_train)
        loss = criterion(outputs, y_train)
        loss.backward()
        optimizer.step()

    st.success("Model trained!")
    st.write(f"Final loss: {loss.item():.4f}")

# Prediction section
st.header("Make Predictions")
input_value = st.number_input("Enter a value for X:", value=5.0)

if st.button("Predict"):
    model.eval()
    with torch.no_grad():
        prediction = model(torch.tensor([[input_value]], dtype=torch.float32))
    st.write(f"Predicted Y value: {prediction.item():.4f}")
