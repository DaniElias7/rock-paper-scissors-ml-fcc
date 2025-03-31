# The ideal response dictionary maps an opponent's predicted move to the move that beats it.
ideal_response = {'P': 'S', 'R': 'P', 'S': 'R'}

def player(prev_opponent_play, 
           opponent_history=[], 
           # Dictionary to store patterns: {'RR': {'R': 1, 'P': 5, 'S': 2}, 'RP': {...}}
           # Keys are opponent move sequences, values are dictionaries counting opponent's subsequent moves.
           play_order={}): 

    # --- Initialization and History Update ---
    if not prev_opponent_play:  # If it's the first move of the match
        # Reset opponent history and pattern tracking for the new match
        opponent_history.clear()
        play_order.clear() 
        # For the very first guess, we can choose randomly or use a fixed start. 'R' is common.
        guess = 'R' 
        return guess
    else:
        # Add the opponent's last move to their history
        opponent_history.append(prev_opponent_play)

    # --- Learn Patterns from History ---
    # We want to learn: "After sequence X, the opponent tends to play move Y"
    # We look at sequences of different lengths (up to a max_len) ending *before* the last opponent move.
    max_len = 4 # Consider opponent sequences up to length 4
    history_len = len(opponent_history)

    # Update the play_order dictionary based on the latest move
    # Example: If history is [R, P, S] and prev_opponent_play is P (history becomes [R, P, S, P])
    # We update counts for:
    #  - Sequence "S" was followed by "P"
    #  - Sequence "PS" was followed by "P"
    #  - Sequence "RPS" was followed by "P"
    if history_len > 1: # Need at least one previous move to form a sequence
        for k in range(1, min(max_len + 1, history_len)): # k is the length of the sequence *before* the last move
            # sequence = "".join(opponent_history[-(k+1):-1]) # Correct slicing to get sequence before the last move
            # Example: history = [R, P, S, P], k = 1. Slice is [-2:-1] -> ['S']. Sequence = "S"
            # Example: history = [R, P, S, P], k = 2. Slice is [-3:-1] -> ['P', 'S']. Sequence = "PS"
            # Example: history = [R, P, S, P], k = 3. Slice is [-4:-1] -> ['R', 'P', 'S']. Sequence = "RPS"
            
            # Simpler way to get the sequence ending just before the last move:
            sequence = "".join(opponent_history[history_len - k - 1 : history_len - 1])
            move_that_followed = prev_opponent_play # The move that came *after* this sequence

            # Initialize dictionary entries if they don't exist
            if sequence not in play_order:
                play_order[sequence] = {}
            if move_that_followed not in play_order[sequence]:
                play_order[sequence][move_that_followed] = 0
            
            # Increment the count for the move that followed the sequence
            play_order[sequence][move_that_followed] += 1

    # --- Make Prediction ---
    # Predict the opponent's *next* move based on the *current* last sequence(s) in their history.
    # Start checking from the longest possible sequence downwards.
    prediction = None
    for k in range(min(max_len, history_len), 0, -1): # Check lengths from max_len down to 1
        # Current last sequence of length k
        current_last_sequence = "".join(opponent_history[-k:]) 
        
        # Check if we have recorded what the opponent did *after* this sequence previously
        if current_last_sequence in play_order:
            # Get the counts of moves that followed this sequence
            potential_next_opponent_moves = play_order[current_last_sequence]
            # Predict the opponent will play the move they played most frequently after this sequence
            prediction = max(potential_next_opponent_moves, key=potential_next_opponent_moves.get)
            # If we found a prediction based on this length sequence, stop checking shorter ones
            break 

    # --- Determine Our Move ---
    if prediction:
        # If we have a prediction, play the move that beats it
        guess = ideal_response[prediction]
    else:
        # Fallback strategy if no pattern matched (e.g., early in the game or unpredictable opponent)
        # Options: random, counter last move, fixed guess. 'S' or 'R' are common successful fallbacks here.
        guess = 'S' # Using 'S' as the fallback guess

    return guess