import torch
import torch.optim as optim
from model import RNASecondaryStructureTransformer
from encode_data import rna_to_one_hot, dot_bracket_to_labels
import torch.nn as nn

# Example data (batch of RNA sequences and corresponding dot-bracket notations)
train_rna = ["AUGCGUAGC", "GGCUAUGCG", "CGUAGCAGC"]
train_structures = [".....(((....)))", "....(((....)))", "....(((....)))"]

# Convert data to tensors
sequences = [rna_to_one_hot(seq) for seq in train_rna]
structures = [dot_bracket_to_labels(structure) for structure in train_structures]

# Find max sequence length (maximum of both RNA sequences and labels)
max_len = max(len(seq) for seq in sequences)  # Find the maximum length in the sequences

# Padding sequences and labels for consistent length
sequences = [rna_to_one_hot(seq, max_len) for seq in train_rna]
structures = [dot_bracket_to_labels(structure, max_len) for structure in train_structures]

# Create attention mask (1 for real data, 0 for padding)
masks = [torch.ones(seq.shape[0]) for seq in sequences]
masks = [torch.cat([mask, torch.zeros(max_len - len(mask))]) for mask in masks]

# Stack the padded sequences and labels into batches
batch_inputs = torch.stack(sequences).permute(1, 0, 2)  # Shape: (seq_len, batch_size, input_dim)
batch_labels = torch.stack(structures)  # Shape: (batch_size, seq_len)
batch_masks = torch.stack(masks)  # Shape: (batch_size, seq_len)

# Initialize the model, loss function, optimizer, and learning rate scheduler
model = RNASecondaryStructureTransformer(input_dim=4, model_dim=128, num_heads=8, num_layers=6, output_dim=3, dropout=0.1)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.5)

# Training loop with gradient clipping and learning rate scheduler
num_epochs = 20
for epoch in range(num_epochs):
    model.train()
    optimizer.zero_grad()
    
    # Forward pass
    outputs = model(batch_inputs, mask=batch_masks.bool())  # Apply mask for padding
    
    # Reshape for loss calculation (we need to compare each timestep output to its label)
    outputs = outputs.view(-1, outputs.shape[2])  # Shape: (seq_len * batch_size, output_dim)
    batch_labels = batch_labels.view(-1)  # Shape: (seq_len * batch_size)
    
    # Calculate loss
    loss = criterion(outputs, batch_labels)
    
    # Backward pass and optimization
    loss.backward()
    
    # Gradient clipping to avoid exploding gradients
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
    
    optimizer.step()
    scheduler.step()
    
    print(f"Epoch [{epoch + 1}/{num_epochs}], Loss: {loss.item():.4f}")


# Model inference function
def predict_secondary_structure(rna_sequence):
    model.eval()  # Set the model to evaluation mode
    one_hot_rna = rna_to_one_hot(rna_sequence, max_len=50).unsqueeze(0).permute(1, 0, 2)  # Add batch dimension
    output = model(one_hot_rna)
    
    # Get the predicted structure (choose the character with highest probability for each position)
    _, predicted_labels = torch.max(output, dim=2)
    
    # Convert predicted labels back to dot-bracket notation
    label_to_char = {0: '.', 1: '(', 2: ')'}
    predicted_structure = ''.join([label_to_char[label.item()] for label in predicted_labels.squeeze()])
    
    return predicted_structure

# Example inference
predicted_structure = predict_secondary_structure("AUGCGUAGC")
print(f"Predicted Structure: {predicted_structure}")
