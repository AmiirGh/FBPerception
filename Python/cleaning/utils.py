import pandas as pd
import os
from typing import List, Dict
import pandas as pd
from voice_reader import *
import re
from time import sleep
import warnings
import random
from pathlib import Path
import shutil
warnings.filterwarnings("ignore")
def extract_dynamic_obstacle_trials(df):
    """
    Detects rising edge in 'is_dynamic_obstacle_present' column and returns a DataFrame
    with only the valid perception rows (where the dynamic obstacle state rises from False to True).
    The feedback_modality is taken from the row immediately after the rise.
    """
    df = df.copy()

    # Ensure boolean
    df["is_dynamic_obstacle_present"] = df["is_dynamic_obstacle_present"].astype(bool)

    # Detect rising edge: FALSE → TRUE
    df["dynamic_rise"] = (
        df["is_dynamic_obstacle_present"]
        & ~df["is_dynamic_obstacle_present"].shift(1, fill_value=False)
    )

    # Set feedback_modality from the next row
    df.loc[df["dynamic_rise"], "feedback_modality"] = (
        df["feedback_modality"].shift(-1)
    )

    # Keep only valid perception rows
    trials = df[df["dynamic_rise"]].copy()
    return trials


def compute_trial_delays(df: pd.DataFrame, phase_number: int):

    if phase_number == 1:
        start_trial = df.query('interval_number == 0 and trial_number == 0').iloc[0]
        start_cue = df.query('interval_number == 1 and trial_number == 1').iloc[0]
        start_trial_time = start_trial['timestamp']
        start_cue_time = start_cue['timestamp']


    else:
        interval_num = (phase_number - 1) * 72 + 1
        query = df.query(f'interval_number == {interval_num} and trial_number == {interval_num-1}')
        cur = query.iloc[0]
        try:
            next = query.iloc[1]
            start_phase = cur if next['timestamp'] - cur['timestamp'] < 15 else next
        except:
            start_phase = cur
        start_cue = df.query(f'interval_number == {interval_num} and trial_number == {interval_num}').iloc[0]
        start_trial_time = start_phase['timestamp']
        start_cue_time = start_cue['timestamp']

    return start_cue_time - start_trial_time


    # if phase_number == 2:
    #     start_trial = df.query('interval_number == 73 and trial_number == 72').iloc[0]
    #     start_cue = df.query('interval_number == 73 and trial_number == 73').iloc[0]
    #     start_trial_time = start_trial['timestamp']
    #     start_cue_time = start_cue['timestamp']
    #     print(f'phase2 added time: {start_cue_time - start_trial_time}')
    #     return start_cue_time - start_trial_time
    #
    # elif phase_number == 3:
    #     query = df.query('interval_number == 145 and trial_number == 144')
    #     start_trial_0 = query.iloc[0]
    #     start_trial_1 = query.iloc[1]
    #     if start_trial_1['timestamp']-start_trial_0['timestamp'] > 20:
    #         ind = 1
    #     else:
    #         ind = 0
    #
    #     start_trial = query.iloc[ind]
    #     start_cue = df.query('interval_number == 145 and trial_number == 145').iloc[0]
    #     start_trial_time = start_trial['timestamp']
    #     start_cue_time = start_cue['timestamp']
    #     print(f'phase3 added time: {start_cue_time - start_trial_time}')
    #     return start_cue_time - start_trial_time


def create_relative_stamps(trials: pd.DataFrame, full_df: pd.DataFrame):
    # Create a mask for reset points
    reset_mask = trials['interval_number'].isin([73, 145])
    # Get indices where resets occur
    reset_indices = trials[reset_mask].index
    # Create cumulative group based on resets
    trials['group'] = 0
    for idx in reset_indices:
        trials.loc[idx:, 'group'] += 1

    # Calculate relative timestamp (starts at 0 for each group)
    def test(x):
        m = x - x.iloc[0]
        return m
    trials['relative_timestamp'] = trials.groupby('group')['timestamp'].transform(test)

    # Add phase-specific delays
    for group_num, phase in enumerate([1, 2, 3]):
        if phase == 3:
            pass
        delay = compute_trial_delays(full_df, phase)
        # print(f'delay for phase {phase} is {delay}')
        group_mask = trials['group'] == group_num
        trials.loc[group_mask, 'relative_timestamp'] += delay

    # Clean up
    trials = trials.drop('group', axis=1)
    trials = trials.reset_index()
    return trials


def find_anomaly(
        df_trials: pd.DataFrame,
        perceived_values: List[Dict],
        start_idx: int,
        base_delay: float,
        tolerance: float = 0.2
):
    corrected_values = []

    # pointer over perceived_values
    pv_idx = 0

    phase_end = start_idx + 72


    for trial_idx in range(start_idx, phase_end):
        if trial_idx == 39:
            pass
        # current cue timestamp
        current_time = df_trials.loc[trial_idx, 'relative_timestamp']

        if trial_idx + 1 < len(df_trials):
            next_time = df_trials.loc[trial_idx + 1, 'relative_timestamp']
        else:
            next_time = current_time + 10  # arbitrary large gap for the last trial

        if trial_idx == 71: next_time = current_time + 13
        elif trial_idx == 143: next_time = current_time + 13
        elif trial_idx == 215:
            next_time = current_time + 13
        if trial_idx == 214:
            pass
        if next_time < current_time:
            print(f' next_time < current_time index is {trial_idx}')
            continue

        # response window
        window_start = current_time
        window_end = next_time + tolerance

        matches = []

        # collect all perceived values inside this window
        while pv_idx < len(perceived_values):

            pv = perceived_values[pv_idx]

            shifted_start = (pv['start_ms'] / 1000) + base_delay
            shifted_end = (pv['end_ms'] / 1000) + base_delay

            # speech before current window
            if shifted_end < window_start:
                pv_idx += 1
                continue

            # speech after window -> stop checking
            if shifted_start > window_end:
                break

            # speech inside window
            matches.append(pv)
            pv_idx += 1

        # ====================================================
        # CASE 1: MISSING RESPONSE
        # ====================================================
        if len(matches) == 0:


            corrected_values.append({
                'degree': 0,
                'level': 0,
                'start_ms': 0,
                'end_ms': 0,
                'text': '0 0'
            })

        # ====================================================
        # CASE 2: NORMAL RESPONSE
        # ====================================================
        elif len(matches) == 1:

            corrected_values.append(matches[0])

        # ====================================================
        # CASE 3: MULTIPLE RESPONSES
        # ====================================================
        else:
            for j, m in enumerate(matches):
                shifted_start = (m['start_ms'] / 1000) + base_delay
                shifted_end = (m['end_ms'] / 1000) + base_delay

            # keep FIRST response only
            corrected_values.append(matches[0])

    return corrected_values


def append_voice_stamps(df_trials: pd.DataFrame, perceived_values: Dict, base_delay: float, phase: int, subject_name: str):

    # Determine the starting index based on part
    if 'degree_perceived' not in df_trials.columns: df_trials['degree_perceived'] = pd.NA

    if 'level_perceived' not in df_trials.columns: df_trials['level_perceived'] = pd.NA

    if 'voice_start' not in df_trials.columns: df_trials['voice_start'] = pd.NA

    if 'voice_end' not in df_trials.columns: df_trials['voice_end'] = pd.NA

    start_idx = (phase-1) * 72
    if len(perceived_values) != 72 or subject_name == 'Navid_4966' or subject_name == 'Asal_6565':
        #print(f'len perceived_values is {len(perceived_values)} ' + 'performing anomaly correction')
        # if phase == 3:
        #     pass
        perceived_values = find_anomaly(df_trials, perceived_values, start_idx, base_delay)

    for i, perceived_value in enumerate(perceived_values):
        row_idx = start_idx + i
        if row_idx >= len(df_trials):
            break

        degree_perceived, level_perceived = perceived_value['text'].split()
        # try:
        #
        # except:
        #     degree_perceived, level_perceived = '8888', '8888'


        df_trials.loc[row_idx, 'degree_perceived'] = int(degree_perceived)

        df_trials.loc[row_idx, 'level_perceived'] = int(level_perceived)


        voice_stamp_start = perceived_values[row_idx % 72]['start_ms'] / 1000

        voice_stamp_end = perceived_values[row_idx % 72]['end_ms'] / 1000
        if voice_stamp_start != 0: # If it is zero, means it was missed so shouldnt add the base_delay to get absolute 0
            voice_stamp_start += base_delay
        if voice_stamp_end != 0:
            voice_stamp_end += base_delay

        df_trials.loc[row_idx, 'voice_start'] = voice_stamp_start
        df_trials.loc[row_idx, 'voice_end'] = voice_stamp_end

    cols = df_trials.columns.tolist()

    # Remove the perceived columns from their current position
    cols.remove('degree_perceived')
    cols.remove('level_perceived')

    # Find positions of degree and level
    degree_idx = cols.index('degree')
    level_idx = cols.index('level')

    # Insert perceived columns after their originals
    cols.insert(degree_idx + 1, 'degree_perceived')
    cols.insert(level_idx + 2, 'level_perceived')  # +2 because we already inserted degree_perceived

    df_trials = df_trials[cols]

    return df_trials


def add_setup_misses(df_trials, subject_setup_misses):
    if pd.isna(subject_setup_misses) or not str(subject_setup_misses).strip():
        return df_trials

    # Extract either:
    # - ranges like [2,7]
    # - single integers like 1
    misses = re.findall(r'\[\s*\d+\s*,\s*\d+\s*\]|\d+', str(subject_setup_misses))

    for miss in misses:

        # Case 1: ranges like [2,7]
        if miss.startswith('['):
            a, b = map(int, re.findall(r'\d+', miss))

            mask = ((df_trials['trial_number'] >= a) & (df_trials['trial_number'] <= b))

        else:
            miss = int(miss)

            mask = (df_trials['trial_number'] == miss)

        # Set perceived values to -1
        df_trials.loc[mask, ['degree_perceived', 'level_perceived']] = -1

    return df_trials




