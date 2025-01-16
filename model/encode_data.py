import numpy as np
import torch

# just in case I need to standardize seq len
def rna_to_one_hot(rna_sequence, max_len=None):
    nucleotides = {'A': 0, 'U': 1, 'G': 2, 'C': 3}

    one_hot = np.zeros((len(rna_sequence), 4))  # 4 for A, U, G, C
    for i, nt in enumerate(rna_sequence):
        if nt in nucleotides:
            one_hot[i, nucleotides[nt]] = 1
    if max_len is not None:
        # Pad sequences to max_len
        one_hot = np.pad(one_hot, ((0, max_len - len(rna_sequence)), (0, 0)), 'constant')
    return torch.tensor(one_hot, dtype=torch.float)


# Convert dot-bracket notation to numeric labels . = 0, ( = 1, ) = 2
def dot_bracket_to_labels(dot_bracket, max_len=None):
    labels = {'.': 0, '(': 1, ')': 2}
    numeric_labels = [labels[char] for char in dot_bracket]
    if max_len is not None:
        # Pad to max_len
        numeric_labels.extend([0] * (max_len - len(numeric_labels)))
    return torch.tensor(numeric_labels, dtype=torch.long)