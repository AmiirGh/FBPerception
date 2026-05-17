import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import re


degrees_dict = {
    'صفر' : 77 ,
    '۱': 1, '1': 1, 'یک': 1, 'یک،': 1,
    '۲': 2, '2': 2, 'دو': 2, 'دو،': 2, 'دوی': 2,
    '۳': 3, '3': 3, 'سه': 3, 'سه،': 3,
    '۴': 4, '4': 4, 'چهار': 4, 'چهار،': 4,
    '۵': 5, '5': 5, 'پنج': 5, 'پنجه': 5, 'پنج،': 5,
    '۶': 6, '6': 6, 'شش،': 6, 'شیش': 6, 'شیشه': 6, 'شش': 6, 'شیش،': 6,
    '۷': 7, '7': 7, 'هفت': 7, 'هفته': 7, 'هفت،': 7,
    '۸': 8, '8': 8, 'هشت': 8, 'هشت،': 8
}

levels_dict = {
    'نزد': 77,
    'نزدیک': 1, 'نزدیک؟': 1, 'قوی': 1,
    'دور': 3, 'دور؟': 3, 'ضعیف؟': 3, 'ضعیف': 3,
    'وسط': 2, 'متوسط': 2, 'وسط؟': 2, 'متوسط؟': 2}

def load_and_process(file_path):
    with open(f'{file_path}', 'r', encoding='utf-8') as f:
        voice = json.load(f)

    text_arr = re.split(r'\.\.\.|\.|؟', voice['text'])
    text_arr = [s.strip() for s in text_arr if s.strip()]

    return text_arr, voice

def merge_tokens_to_text(text_arr, tokens):
    """
    Merge tokens to match text_arr elements and extract start_ms and end_ms
    
    Args:
        text_arr: List of text strings to match
        tokens: List of token dictionaries with 'text', 'start_ms', 'end_ms', etc.
    
    Returns:
        List of dictionaries with merged token information
    """
    result = []
    token_idx = 0
    
    for text in text_arr:
        # Clean the target text (remove extra spaces)
        target_text = text.strip()
        
        # Skip empty strings
        if not target_text:
            continue
        
        # Collect tokens that make up this text
        collected_tokens = []
        accumulated_text = ""
        start_idx = token_idx
        
        while token_idx < len(tokens):
            token = tokens[token_idx]
            token_text = token['text']
            if token_text == '.' or token_text == '...' or token_text == '?' or token_text == '؟':
                token_idx +=1
                continue
            
            # Add token to accumulated text
            accumulated_text += token_text
            collected_tokens.append(token)
            token_idx += 1
            
            # Clean accumulated text for comparison
            cleaned_accumulated = accumulated_text.strip().replace(' ', '')
            cleaned_target = target_text.replace(' ', '')
            
            # Check if we've matched the target text
            if cleaned_accumulated == cleaned_target:
                break
            
            # Check if accumulated text contains the target (for partial matches)
            if cleaned_target in cleaned_accumulated or cleaned_accumulated in cleaned_target:
                # If we have enough match, break
                if len(cleaned_accumulated) >= len(cleaned_target):
                    break
        
        # Create merged result
        if collected_tokens:
            merged = {
                'text': target_text,
                'start_ms': collected_tokens[0]['start_ms'],
                'end_ms': collected_tokens[-1]['end_ms'],
                'confidence': sum(t['confidence'] for t in collected_tokens) / len(collected_tokens),
            }
            result.append(merged)
    
    return result


def extract_degree_levels(text_arr, degrees_dict, levels_dict):
    print(degrees_dict)
    """
    Extracts degree and level information from a list of text entries.
    
    Args:
        text_arr (list of str): List of text strings to process.
        degrees_dict (dict): Mapping of keywords to degree names.
        levels_dict (dict): Mapping of keywords to level names.
        
    Returns:
        list of str: List of combined "degree level" strings.
    """
    result = []
    i = 0
    
    while i < len(text_arr):
        # Clean text
        text = text_arr[i].strip()
        words = text.split()
        
        degree = None
        level = None
        
        # Check current text for matches
        for w in words:
            if w in degrees_dict:
                degree = degrees_dict[w]
            elif w in levels_dict:
                level = levels_dict[w]

        
        # Lookahead to next entry if nothing found
        if (degree is None or level is None) and i + 1 < len(text_arr):
            next_words = text_arr[i+1].strip().split()
            for w in next_words:
                if degree is None and w in degrees_dict:
                    degree = degrees_dict[w]
                if level is None and w in levels_dict:
                    level = levels_dict[w]
            # Skip next entry if it contributed
            if degree is not None or level is not None:
                i += 1
        
        if degree is not None or level is not None:
            degree = degree or ''
            level = level or ''
            result.append(f"{degree} {level}".strip())
        
        i += 1
    
    return result

def extract_degree_levels(text_arr, degrees_dict, levels_dict):
    result = []
    i = 0
    
    while i < len(text_arr):
        # Clean text
        text = text_arr[i]['text'].strip()
        words = text.split()
        # print(words)
        degree = None
        level = None
        
        # Get timing info from current entry
        start_ms = text_arr[i]['start_ms']
        end_ms = text_arr[i]['end_ms']

        if len(words) != 2:
            i += 1
            continue

        # Check current text for matches
        for w in words:
            if w in degrees_dict:
                degree = degrees_dict[w]
            elif w in levels_dict:
                level = levels_dict[w]
        
        # Lookahead to next entry if nothing found
        if (degree is None or level is None) and i + 1 < len(text_arr):
            next_words = text_arr[i+1]['text'].strip().split()
            for w in next_words:
                if w in degrees_dict: #degree is None and w in degrees_dict:
                    degree = degrees_dict[w]
                if w in levels_dict: #level is None and w in levels_dict:
                    level = levels_dict[w]
            # If next entry contributed, extend timing to include it
            if degree is not None and level is not None:
                end_ms = text_arr[i+1]['end_ms']  # Update end time
                i += 1  # Skip next entry
        
        if degree is not None and level is not None:
            degree = degree or ''
            level = level or ''
            result.append({
                "degree": degree,
                "level": level,
                "start_ms": start_ms,
                "end_ms": end_ms,
                "text": f"{degree} {level}".strip()  # Optional: keep combined text
            })
        
        i += 1
    
    # print(f'len result: {len(result)}')
    return result


