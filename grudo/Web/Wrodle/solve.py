import os
import requests
import time

URL = "http://10.112.0.12:44574"

def load_words():
    # Load real answers and all words
    real_answers_path = "/home/light/Workspace/CTF/grudo/Web/Wrodle/real_answers.txt"
    all_words_path = "/home/light/Workspace/CTF/grudo/Web/Wrodle/words.txt"
    
    real_answers = []
    if os.path.exists(real_answers_path):
        with open(real_answers_path, 'r') as f:
            for line in f:
                w = line.strip().lower()
                if w and not w.startswith('#') and len(w) == 5 and w.isalpha():
                    real_answers.append(w)
                    
    all_words = []
    if os.path.exists(all_words_path):
        with open(all_words_path, 'r') as f:
            for line in f:
                w = line.strip().lower()
                if w and not w.startswith('#') and len(w) == 5 and w.isalpha():
                    all_words.append(w)
                    
    # Ensure uniqueness
    real_answers = list(set(real_answers))
    all_words = list(set(all_words))
    
    if not real_answers:
        real_answers = list(all_words)
        
    return real_answers, all_words

def generate_feedback(target, guess):
    feedback = ['absent'] * 5
    t_list = list(target)
    
    # First pass: correct letters
    for i in range(5):
        if guess[i] == target[i]:
            feedback[i] = 'correct'
            t_list[i] = None
            
    # Second pass: present letters
    for i in range(5):
        if feedback[i] != 'correct':
            g_char = guess[i]
            try:
                idx = t_list.index(g_char)
                feedback[i] = 'present'
                t_list[idx] = None
            except ValueError:
                pass
                
    return feedback

def filter_candidates(candidates, guesses_history):
    filtered = list(candidates)
    for guess, feedback in guesses_history:
        filtered = [c for c in filtered if generate_feedback(c, guess) == feedback]
    return filtered

def choose_best_partition_guess(candidates):
    best_g = None
    min_expected_size = float('inf')
    
    # If the candidate list is small, check all candidates.
    # Otherwise, to save time, sample a subset of candidates to evaluate as guesses.
    search_space = candidates
    if len(candidates) > 150:
        # Sort by frequency score first and take the top 100 to evaluate
        freqs = {}
        for w in candidates:
            for char in set(w):
                freqs[char] = freqs.get(char, 0) + 1
        scored = []
        for w in candidates:
            score = sum(freqs.get(char, 0) for char in set(w))
            scored.append((score, w))
        scored.sort(reverse=True)
        search_space = [w for _, w in scored[:100]]
        
    for g in search_space:
        feedback_counts = {}
        for c in candidates:
            fb = tuple(generate_feedback(c, g))
            feedback_counts[fb] = feedback_counts.get(fb, 0) + 1
        expected_size = sum(count**2 for count in feedback_counts.values())
        if expected_size < min_expected_size:
            min_expected_size = expected_size
            best_g = g
            
    return best_g

def choose_best_freq_guess(candidates):
    freqs = {}
    for w in candidates:
        for char in set(w):
            freqs[char] = freqs.get(char, 0) + 1
            
    best_g = None
    max_score = -1
    for w in candidates:
        score = sum(freqs.get(char, 0) for char in set(w))
        if score > max_score:
            max_score = score
            best_g = w
    return best_g

def main():
    real_answers, all_words = load_words()
    print(f"Loaded {len(real_answers)} real answers and {len(all_words)} total words.")
    
    with open("solved_words.txt", "w") as f:
        pass
        
    r = requests.post(f"{URL}/api/start")
    if r.status_code != 200:
        print("Failed to start session:", r.text)
        return
        
    data = r.json()
    token = data.get("token")
    headers = {"Authorization": f"Bearer {token}"}
    
    print("Session started. Token:", token[:20] + "...")
    print("Initial State:", data)
    
    current_word_idx = data.get("current_word", 1)
    lives = data.get("lives", 9)
    total_words = data.get("total_words", 50)
    
    guesses_history = []
    candidates_source = "real"
    candidates = list(real_answers)
    
    invalid_guesses = set()
    
    while True:
        if data.get("done"):
            print("All words solved! Getting final hint...")
            finish_res = requests.get(f"{URL}/api/finish", headers=headers)
            print("Finish Response:", finish_res.json())
            break
            
        print(f"\n--- Word {current_word_idx} / {total_words} ---")
        print(f"Lives: {lives}, Attempts on server: {data.get('attempts', 0)}")
        
        # Filter candidates
        candidates = filter_candidates(real_answers if candidates_source == "real" else all_words, guesses_history)
        candidates = [c for c in candidates if c not in invalid_guesses]
        
        print(f"Candidates remaining ({candidates_source}): {len(candidates)}")
        if len(candidates) < 15:
            print("Remaining candidates:", candidates)
            
        if len(candidates) == 0:
            if candidates_source == "real":
                print("No candidates left in real answers. Falling back to all words...")
                candidates_source = "all"
                candidates = filter_candidates(all_words, guesses_history)
                candidates = [c for c in candidates if c not in invalid_guesses]
                print(f"Candidates in all words: {len(candidates)}")
                if len(candidates) < 15:
                    print("Remaining candidates:", candidates)
            
            if len(candidates) == 0:
                print("WARNING: No candidates left at all! Resetting history for this word.")
                guesses_history = []
                candidates = [w for w in all_words if w not in invalid_guesses]
                candidates_source = "all"
                
        # Choose guess
        if len(guesses_history) == 0:
            guess = "tares"
        elif len(candidates) == 1:
            guess = candidates[0]
        elif len(candidates) == 2:
            guess = candidates[0]
        elif len(candidates) <= 300:
            guess = choose_best_partition_guess(candidates)
        else:
            guess = choose_best_freq_guess(candidates)
            
        print(f"Guessing: {guess}")
        
        r = requests.post(f"{URL}/api/guess", headers=headers, json={"guess": guess})
        if r.status_code == 400:
            res_json = r.json()
            if res_json.get("error") == "not in word list":
                print(f"Server rejected guess '{guess}' (not in word list). Removing from dictionary...")
                invalid_guesses.add(guess)
                if guess in all_words:
                    all_words.remove(guess)
                if guess in real_answers:
                    real_answers.remove(guess)
                continue
            else:
                print("Error 400:", res_json)
                break
        elif r.status_code != 200:
            print(f"HTTP Error {r.status_code}: {r.text}")
            break
            
        res_json = r.json()
        if "token" in res_json:
            token = res_json["token"]
            headers["Authorization"] = f"Bearer {token}"
        print("Feedback:", res_json.get("feedback"))
        
        if res_json.get("reset"):
            print("GAME RESET! Starting over from word 1.")
            with open("solved_words.txt", "w") as f:
                pass
            guesses_history = []
            candidates_source = "real"
            invalid_guesses = set()
            data = res_json
            current_word_idx = data.get("current_word", 1)
            lives = data.get("lives", 9)
            continue
            
        if res_json.get("correct"):
            print("Correct! Moving to next word.")
            with open("solved_words.txt", "a") as f:
                f.write(guess + "\n")
            guesses_history = []
            candidates_source = "real"
            data = res_json
            current_word_idx = data.get("current_word", 1)
            lives = data.get("lives", 9)
            time.sleep(0.05)
            continue
            
        if res_json.get("wordFailed"):
            print("Word failed (6 attempts burned). Lost 1 life. Retrying the same word...")
            data = res_json
            lives = data.get("lives", 9)
            continue
            
        guesses_history.append((guess, res_json.get("feedback")))
        data = res_json
        lives = data.get("lives", 9)
        time.sleep(0.05)

if __name__ == "__main__":
    main()
