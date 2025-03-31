import random

# Maps an anticipated opponent move to the move that wins against it.
COUNTER_MOVE = {'P': 'S', 'R': 'P', 'S': 'R'}
POSSIBLE_MOVES = ['R', 'P', 'S']

# --- Configuration ---
# How far back to look in the opponent's history for patterns.
MAX_SEQUENCE_LENGTH = 4 

def player(prev_opponent_play, 
           opponent_history=[], 
           # Stores observed patterns: keys are opponent move sequences (e.g., "RP"), 
           # values are dicts mapping the *next* move ('R','P','S') to its frequency.
           learned_patterns={}):
    """
    Predicts the opponent's next move based on historical patterns 
    and plays the counter move.

    Manages state (history, patterns) internally using default arguments.
    State is reset when prev_opponent_play is empty (first call for a match).

    Args:
        prev_opponent_play: The opponent's last move ('R', 'P', 'S', or empty).
        opponent_history: List to store opponent's move history (managed internally).
        learned_patterns: Dict to store patterns (managed internally).

    Returns:
        The bot's next move ('R', 'P', or 'S').
    """

    # --- State Management & History Update ---
    if not prev_opponent_play:
        # First move of a new match, reset history and learned patterns.
        opponent_history.clear()
        learned_patterns.clear()
        # Start with a default or random move for the very first round.
        return random.choice(POSSIBLE_MOVES) 
    else:
        # Add the opponent's actual last move to the history.
        opponent_history.append(prev_opponent_play)

    # --- Update Learning Model ---
    history_len = len(opponent_history)
    # Only update patterns if we have enough history to form a sequence 
    # plus the move that followed it.
    if history_len > 1: 
        # Consider sequences of different lengths ending *before* the opponent's last move.
        for k in range(1, min(MAX_SEQUENCE_LENGTH + 1, history_len)):
            # Extract the sequence of length k that occurred right before the last move.
            # Example: history=[R,P,S,P], k=2 -> sequence = "PS"
            sequence = "".join(opponent_history[-(k+1):-1]) 
            move_that_followed = prev_opponent_play

            # Ensure the sequence key exists in the pattern dictionary.
            if sequence not in learned_patterns:
                learned_patterns[sequence] = {'R': 0, 'P': 0, 'S': 0}
            
            # Increment the count for the move that followed this sequence.
            learned_patterns[sequence][move_that_followed] += 1

    # --- Predict Opponent's Next Move ---
    prediction = None
    # Look for patterns matching the *end* of the current history.
    # Start with the longest possible sequence and go shorter.
    for k in range(min(MAX_SEQUENCE_LENGTH, history_len), 0, -1):
        current_sequence = "".join(opponent_history[-k:])
        
        if current_sequence in learned_patterns:
            # Get the recorded frequencies of moves following this sequence.
            move_counts = learned_patterns[current_sequence]
            
            # Check if we have recorded any moves following this sequence.
            if sum(move_counts.values()) > 0:
                # Predict the opponent will repeat their most frequent response.
                prediction = max(move_counts, key=move_counts.get)
                # Found a prediction based on patterns, no need to check shorter sequences.
                break 

    # --- Select Our Move ---
    if prediction:
        # If a prediction was made, play the counter move.
        my_move = COUNTER_MOVE[prediction]
    else:
        # Fallback: If no pattern was predictive, counter the opponent's absolute last move.
        # This provides a basic level of reactivity.
        my_move = COUNTER_MOVE[prev_opponent_play]

    return my_move