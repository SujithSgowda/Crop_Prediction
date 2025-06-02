import pandas as pd
import numpy as np
import joblib
import sys

# Define header based on the input structure
header = ['State_Name', 'District_Name', 'Season', 'Crop'] 

# Question class handles decision tree node evaluation
class Question:
    def __init__(self, column, value):
        self.column = column
        self.value = value

    def match(self, example):
        val = example[self.column]
        return val == self.value

    def __repr__(self):
        return "Is %s %s %s?" % (
            header[self.column], "==", str(self.value))


# Calculate the class counts in a dataset (for prediction purposes)
def class_counts(data):
    counts = {}
    for row in data:
        label = row[-1]
        if label not in counts:
            counts[label] = 0
        counts[label] += 1
    return counts


# Leaf node class stores predictions
class Leaf:
    def __init__(self, data):
        self.predictions = class_counts(data)


# Decision node stores questions and branches (True/False)
class Decision_Node:
    def __init__(self, question, true_branch, false_branch):
        self.question = question
        self.true_branch = true_branch
        self.false_branch = false_branch


# Function to print the tree
def print_tree(node, spacing=""):
    if isinstance(node, Leaf):
        print(spacing + "Predict", node.predictions)
        return
    print(spacing + str(node.question))
    print(spacing + "--> True:")
    print_tree(node.true_branch, spacing + "  ")
    print(spacing + "--> False:")
    print_tree(node.false_branch, spacing + "  ")


# Print the leaf node's probabilities
def print_leaf(counts):
    total = sum(counts.values()) * 1.0
    probs = {}
    for lbl in counts.keys():
        probs[lbl] = str(int(counts[lbl] / total * 100)) + "%"
    return probs


# Classify a row by navigating the decision tree
def classify(row, node):
    if isinstance(node, Leaf):
        return node.predictions
    if node.question.match(row):
        return classify(row, node.true_branch)
    else:
        return classify(row, node.false_branch)


# Load the trained decision tree model
try:
    dt_model_final = joblib.load('ML/crop_prediction/filetest2.pkl')
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    sys.exit(1)

# Get command line inputs
if len(sys.argv) < 4:
    print("Usage: script.py <State_Name> <District_Name> <Season>")
    sys.exit(1)

state = sys.argv[1]
district = sys.argv[2]
season = sys.argv[3]

# Test data for prediction
testing_data = [[state, district, season, None]]  # None for crop as it’s what we’re predicting

print(f"Testing data: {testing_data}")

# Classify and predict
for row in testing_data:
    try:
        prediction = classify(row, dt_model_final)
        print(f"Prediction for {row}: {prediction}")
        Predict_dict = print_leaf(prediction).copy()
    except Exception as e:
        print(f"Error during classification: {e}")
        sys.exit(1)

# Print the predictions
for key, value in Predict_dict.items():
    print(f"{key}: {value}")
