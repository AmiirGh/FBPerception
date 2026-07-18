import os
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader


# ---------------------------------------------------------
# 1. Data Loading Functions
# ---------------------------------------------------------

def get_perception_results_df(data_path):
    subjects_data_trials = {}
    for folder_name in sorted(os.listdir(data_path)):
        folder_path = os.path.join(data_path, folder_name)
        if not os.path.isdir(folder_path):
            continue
        csv_path = os.path.join(folder_path, "Perception results.csv")
        if os.path.exists(csv_path):
            trials_data = pd.read_csv(csv_path)
            subjects_data_trials[folder_name] = trials_data
    return subjects_data_trials


def get_experiment_logs_df(data_path):
    subjects_data_logs = {}
    for folder_name in sorted(os.listdir(data_path)):
        folder_path = os.path.join(data_path, folder_name)
        if not os.path.isdir(folder_path):
            continue
        csv_path = os.path.join(folder_path, "Experiment logs.csv")
        if os.path.exists(csv_path):
            logs_data = pd.read_csv(csv_path)
            subjects_data_logs[folder_name] = logs_data
    return subjects_data_logs


# ---------------------------------------------------------
# 2. Neural Network Architecture
# ---------------------------------------------------------

class ModalityConflictUnit(nn.Module):
    """
    Independent pathway for a single modality.
    Uses a recurrent state to pass conflict/interference from time t-1 to time t.
    """

    def __init__(self, input_dim, hidden_dim):
        super(ModalityConflictUnit, self).__init__()
        # Processes spatial cue features (e.g., angle, distance)
        self.feature_extractor = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU()
        )
        # GRUCell acts as the conflict monitor, updating its state based ONLY on this modality
        self.conflict_monitor = nn.GRUCell(hidden_dim, hidden_dim)

        # Output predictors
        self.accuracy_head = nn.Linear(hidden_dim, 1)
        self.rt_head = nn.Linear(hidden_dim, 1)

    def forward(self, x, prev_conflict_state):
        features = self.feature_extractor(x)

        # The conflict state is updated. Interference in trial t-1 affects trial t here.
        current_conflict_state = self.conflict_monitor(features, prev_conflict_state)

        # Predictions
        accuracy = torch.sigmoid(self.accuracy_head(current_conflict_state))
        rt = torch.relu(self.rt_head(current_conflict_state))

        return accuracy, rt, current_conflict_state


class IndependentConflictModel(nn.Module):
    """
    Main architecture connecting the 3 sensory pathways and 1 navigation pathway.
    Demonstrates independent control adaptation per modality.
    """

    def __init__(self, nav_input_dim, cue_input_dim, hidden_dim):
        super(IndependentConflictModel, self).__init__()
        self.hidden_dim = hidden_dim

        # A. Three Independent Sensory Pathways
        self.visual_pathway = ModalityConflictUnit(cue_input_dim, hidden_dim)
        self.auditory_pathway = ModalityConflictUnit(cue_input_dim, hidden_dim)
        self.tactile_pathway = ModalityConflictUnit(cue_input_dim, hidden_dim)

        # B. Navigation Task Processing Pathway
        self.nav_pathway = nn.Sequential(
            nn.Linear(nav_input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU()
        )
        self.nav_output = nn.Linear(hidden_dim // 2, 1)  # Predicts collision likelihood/performance

    def forward(self, nav_x, vis_x, aud_x, tac_x, prev_states):
        vis_prev, aud_prev, tac_prev = prev_states

        # Process navigation independently of modality-specific conflict
        nav_features = self.nav_pathway(nav_x)
        nav_pred = torch.sigmoid(self.nav_output(nav_features))

        # Process modalities. Only the active modality input (vis_x, aud_x, or tac_x)
        # will have non-zero tensors depending on the data preparation step.
        vis_acc, vis_rt, vis_state = self.visual_pathway(vis_x, vis_prev)
        aud_acc, aud_rt, aud_state = self.auditory_pathway(aud_x, aud_prev)
        tac_acc, tac_rt, tac_state = self.tactile_pathway(tac_x, tac_prev)

        return nav_pred, (vis_acc, aud_acc, tac_acc), (vis_rt, aud_rt, tac_rt), (vis_state, aud_state, tac_state)

    def init_hidden_states(self, batch_size):
        # Initialize zero conflict states for the start of an experiment
        return (
            torch.zeros(batch_size, self.hidden_dim),
            torch.zeros(batch_size, self.hidden_dim),
            torch.zeros(batch_size, self.hidden_dim)
        )


# ---------------------------------------------------------
# 3. Model Testing and Data Integration Example
# ---------------------------------------------------------

def test_model_architecture():
    """
    Instantiates the model and passes dummy tensors simulating a batch
    processed from Perception results.csv and Experiment logs.csv to verify execution.
    """
    batch_size = 32
    nav_input_dim = 3  # e.g., Difficulty level (easy=0, med=1, hard=2), Thumbstick_x, Thumbstick_y
    cue_input_dim = 2  # e.g., Target Angle, Target Distance
    hidden_dim = 16

    model = IndependentConflictModel(nav_input_dim, cue_input_dim, hidden_dim)

    # Simulate a batch of data
    nav_inputs = torch.randn(batch_size, nav_input_dim)

    # Simulate cue inputs (only one modality is active per trial in reality; others can be zero-padded)
    vis_inputs = torch.randn(batch_size, cue_input_dim)
    aud_inputs = torch.randn(batch_size, cue_input_dim)
    tac_inputs = torch.randn(batch_size, cue_input_dim)

    # Initialize previous conflict states (from trial t-1)
    prev_states = model.init_hidden_states(batch_size)

    # Forward pass
    nav_pred, acc_preds, rt_preds, next_states = model(
        nav_inputs, vis_inputs, aud_inputs, tac_inputs, prev_states
    )

    print("Forward pass successful.")
    print(f"Navigation Performance Output Shape: {nav_pred.shape}")
    print(f"Visual RT Prediction Shape: {rt_preds[0].shape}")
    print(f"Auditory State Shape (carried to t+1): {next_states[1].shape}")


if __name__ == "__main__":
    # Test architecture viability
    test_model_architecture()

    # Example usage for real data (requires actual directory structure)
    data_path = '../Dataset/Dataset/Recordings'
    perception_dfs = get_perception_results_df(data_path)
    experiment_dfs = get_experiment_logs_df(data_path)
    dataset = prepare_dual_task_dataset(perception_dfs, experiment_dfs)
    train_model(model, dataset)