import torch
import torch.nn as nn
import torch.optim as optim

import numpy as np
import math

class PositionalEncoding(nn.Module):
    def __init__(self, model_dim, dropout=0.1, max_len=5000):
        super(PositionalEncoding, self).__init__()
        
        # matrix for positional encodings
        pe = torch.zeros(max_len, model_dim)
        
        # tensor for positions (0, 1, 2, i, max_len - 1)
        position = torch.arange(0, max_len).float().unsqueeze(1)
        
        # scale position
        div_term = torch.exp(torch.arange(0, model_dim, 2).float() * -(math.log(10000.0) / model_dim))
        
        # Apply the sine and cosine functions on the positions
        # Sin is applied to even indices (0, 2, 4, ...) of the encoding vector
        # Cos is applied to odd indices (1, 3, 5, ...) of the encoding vector
        # This ensures that each position gets a unique encoding.
        pe[:, 0::2] = torch.sin(position * div_term)  # Apply sine to even indices
        pe[:, 1::2] = torch.cos(position * div_term)  # Apply cosine to odd indices
        
        # batch dimension to the encoding tensor
        pe = pe.unsqueeze(0)
        
        # positional encoding tensor as a buffer so it isn't a parameter
        self.register_buffer('pe', pe)
        
        # dropout layer to avoid overfit
        self.dropout = nn.Dropout(p=dropout)

    def forward(self, x):
        """
        The forward method adds the positional encoding to the input tensor `x`.
        The input tensor `x` is expected to have the shape (seq_len, batch_size, model_dim).
        """
        # Add the positional encoding to the input tensor
        x = x + self.pe[:, :x.size(0)]
        
        # Apply dropout to the encoded tensor to prevent overfitting
        return self.dropout(x)


class RNASecondaryStructureTransformer(nn.Module):
    def __init__(self, input_dim=4, model_dim=128, num_heads=8, num_layers=6, output_dim=3, dropout=0.1):
        super(RNASecondaryStructureTransformer, self).__init__()
        
        # Embedding Layer (embedding the one-hot RNA sequence)
        self.embedding = nn.Linear(input_dim, model_dim)
        
        # positional encoding layer
        self.positional_encoding = PositionalEncoding(model_dim, dropout)
        
        # Transformer Encoder
        self.transformer = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(d_model=model_dim, nhead=num_heads, dropout=dropout),
            num_layers=num_layers  # Number of transformer layers
        )
        
        # Output layer (predict dot-bracket labels)
        self.fc_out = nn.Linear(model_dim, output_dim)

    def forward(self, x, mask=None):
        # x is expected to be of shape (seq_len, batch_size, input_dim)
        x = self.embedding(x)  # Shape: (seq_len, batch_size, model_dim)
        
        # Apply positional encoding
        x = self.positional_encoding(x)
        
        # Transformer expects input in shape (seq_len, batch_size, model_dim)
        x = self.transformer(x, src_key_padding_mask=mask)
        
        # Output layer (predict dot-bracket labels)
        x = self.fc_out(x)  # Shape: (seq_len, batch_size, output_dim)
        
        return x