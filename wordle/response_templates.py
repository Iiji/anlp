import os

from platformdirs import user_cache_dir
base_dir = os.path.dirname(__file__)

def analyze_response(guess: str, response: str):
    appreance_counts = {}
    correct_letters = "?" * len(guess)
    letter_wrong_positions = {}
    unused_letters = {}
    for i, char, r in zip(range(len(guess)), guess.upper(), response):
        if r == 'G':
            appreance_counts[char] = appreance_counts.get(char, 0) + 1
            correct_letters= correct_letters[:i] + char + correct_letters[i+1:]
        elif r == 'Y':
            appreance_counts[char] = appreance_counts.get(char, 0) + 1
            letter_wrong_positions[char] = letter_wrong_positions.get(char, []) + [i]

    for i, char, r in zip(range(len(guess)), guess.upper(), response):
        if r == '?':
            if appreance_counts.get(char, 0)>0:
                letter_wrong_positions[char] = letter_wrong_positions.get(char, []) + [i]
            else:
                unused_letters[char] = 1
    
    unused_letters = list(unused_letters.keys())
    return correct_letters, letter_wrong_positions, appreance_counts, unused_letters

def get_ordinal(n: int) -> str:
    if n == 1:
        return '1st'
    elif n == 2:
        return '2nd'
    elif n == 3:
        return '3rd'
    else:
        return f'{n}th'

def get_color(response: str):
    colors = []
    for char in response:
        if char == 'G':
            colors.append('Green')
        elif char == 'Y':
            colors.append('Yellow')
        else:
            colors.append('Gray')
    return colors

def get_guess_explanation(
    guess: str, 
    response: str,
    correct_letters: str,
    letter_wrong_positions: dict,
    appreance_counts: dict,
    unused_letters: list
):
    explanation = []
    for i, char in zip(range(len(guess)), correct_letters):
        if char != '?':
            explanation.append(f"the {get_ordinal(i+1)} letter is {char.upper()}")

    for char, positions in letter_wrong_positions.items():
        if appreance_counts[char] == 1:
            explanation.append(f"letter {char.upper()} appears in the word but not at the {get_ordinal(positions[0]+1)} position")
        else:
            positions = sorted(positions)
            explanation.append(f"letter {char.upper()} appears in the word {appreance_counts[char]} times, but not at the {', '.join(get_ordinal(p+1) for p in positions)} position")

    for char in unused_letters:
        explanation.append(f"letter {char.upper()} does not appear in the word")

    return explanation

def get_unk_position_explanation(
    correct_letters: str,
    letter_wrong_positions: dict,
    appreance_counts: dict,
):
    explanation = []
    for char, positions in letter_wrong_positions.items():
        if appreance_counts[char] > correct_letters.count(char):
            remain_appreance = appreance_counts[char] - correct_letters.count(char)
            valid_positions = [i for i in range(len(correct_letters)) if correct_letters[i] == '?' and i not in positions]
            explanation.append(f"letter {char.upper()} appears in the word {remain_appreance} times, among positions {', '.join([str(p+1) for p in valid_positions])}")
    return explanation


meta_prompt_beta_path = os.path.join(base_dir, 'wordle-meta-beta.md')
meta_prompt_beta = open(meta_prompt_beta_path, 'r').read()
meta_prompt_v0_path = os.path.join(base_dir, 'wordle-meta-v0.md')
meta_prompt_v0 = open(meta_prompt_v0_path, 'r').read()
first_guess_template_v0 = """
My first guess is "{next_word}".
GUESS: {next_word}
"""
guess_sum_last_v0 = """
My last guess is: {guess_word}, whose letters are {guess_letters}.
The color for each letter is: {letter_colors}.
According to the color of letters in the result, we know that: {guess_explain}.
"""
guess_state_v0 = """
Based on my guess history, we currently know:
We have made {num_guesses} guesses, and have {chances_remain} chances left.
Letters at the correct position: {correct_letters}
Letters at unknown position: {unk_positions}.
Letters that do not appear in the word: {unused_letters}.
"""
guess_analyze_v0 = """
Now, I need to make the {i} guess. {simple_analysis}{potential_words}Considering all the information above, my next guess would be "{next_word}".
GUESS: {next_word}
"""

def fill_guess_template_v0(
    current_guess: str, 
    current_response: str,
    attempts: int,
    remaining_attempts: int,
    correct_letters: str,
    letter_wrong_positions: dict,
    appreance_counts: dict,
    unused_letters: list,
    last_guess: str = None, 
    make_guess: bool = True
):

    if last_guess is None:
        # first guess
        if make_guess:
            guess_template = "OK, the game starts. " + first_guess_template_v0.format(next_word=current_guess).strip()
        else:
            guess_template = "OK, the game starts."
        return guess_template, correct_letters, letter_wrong_positions, appreance_counts, unused_letters
    
    c_letters, l_w_positions, a_counts, u_letters = analyze_response(last_guess, current_response)
    # update the guess state
    for i, char in enumerate(c_letters):
        if char != '?':
            correct_letters = correct_letters[:i] + char + correct_letters[i+1:]
    for char, positions in l_w_positions.items():
        letter_wrong_positions[char] = letter_wrong_positions.get(char, []) + positions
        letter_wrong_positions[char] = list(sorted(set(letter_wrong_positions[char])))
    for char, count in a_counts.items():
        appreance_counts[char] = max(appreance_counts.get(char, 0), count)
    for char in u_letters:
        if char not in unused_letters:
            unused_letters.append(char)

    guess_template = ""
    guess_letters = ", ".join(char for char in last_guess.upper())
    letter_colors= ", ".join(get_color(current_response))
    guess_explain = "; ".join(get_guess_explanation(last_guess, current_response,
        correct_letters=c_letters, letter_wrong_positions=l_w_positions, 
        appreance_counts=a_counts, unused_letters=u_letters))
    guess_template += guess_sum_last_v0.format(
        guess_word=last_guess.lower(),
        guess_letters=guess_letters,
        letter_colors=letter_colors,
        guess_explain=guess_explain
    )
    unk_positions = "; ".join(get_unk_position_explanation(
        correct_letters, letter_wrong_positions, appreance_counts))
    guess_template += guess_state_v0.format(
        num_guesses=attempts,
        chances_remain=remaining_attempts,
        correct_letters=correct_letters,
        unk_positions=unk_positions,
        unused_letters=', '.join(unused_letters)
    )
    if make_guess:
        guess_template += guess_analyze_v0.format(
            i=get_ordinal(attempts+1),
            simple_analysis="",
            potential_words="",
            next_word=current_guess
        )

    return guess_template.strip(), correct_letters, letter_wrong_positions, appreance_counts, unused_letters



meta_prompt_v1_path = os.path.join(base_dir, 'wordle-meta-v1.md')
meta_prompt_v1 = open(meta_prompt_v1_path, 'r').read()
guess_sum_last_v1 = """
My last guess is: {guess_word}, whose letters are {guess_letters}.
The color for each letter is: {letter_colors}.
From the colors of letters, we know that: {guess_explain}.
"""
guess_state_v1 = """
Based on the guess history, we can summarize the information below:
Letters at the correct position: {correct_letters}
Letters at unknown position: {unk_positions}.
Letters that do not appear in the word: {unused_letters}.
"""
guess_analyze_v1 = """
Now, I need to make the {i} guess. Considering all the information above, my next guess would be "{next_word}".
GUESS: {next_word}
"""
def fill_user_input_v1(
    step:int, 
    correct_letters: str,
    letter_wrong_positions: dict,
    appreance_counts: dict,
    unused_letters: list,
):
    if step == 0:
        return "Now, the game starts. Please make your 1st guess."
    elif step == 1:
        return "This is the result of your last guess: <image>. Please make your 2nd guess."
    else:
        unk_positions = "; ".join(get_unk_position_explanation(
            correct_letters, letter_wrong_positions, appreance_counts))
        state = guess_state_v1.format(
            num_guesses=step,
            correct_letters=correct_letters,
            unk_positions=unk_positions,
            unused_letters=', '.join(unused_letters)
        )
        return f"This is the result of your last guess: <image>.{state}Please make your {get_ordinal(step+1)} guess.".strip()

def fill_guess_template_v1(
    current_guess: str, 
    current_response: str,
    attempts: int,
    remaining_attempts: int,
    correct_letters: str,
    letter_wrong_positions: dict,
    appreance_counts: dict,
    unused_letters: list,
    last_guess: str = None, 
    make_guess: bool = True
):
    guess_template = ""

    if last_guess is not None:
        c_letters, l_w_positions, a_counts, u_letters = analyze_response(last_guess, current_response)
        # update the guess state
        for i, char in enumerate(c_letters):
            if char != '?':
                correct_letters = correct_letters[:i] + char + correct_letters[i+1:]
        for char, positions in l_w_positions.items():
            letter_wrong_positions[char] = letter_wrong_positions.get(char, []) + positions
            letter_wrong_positions[char] = list(sorted(set(letter_wrong_positions[char])))
        for char, count in a_counts.items():
            appreance_counts[char] = max(appreance_counts.get(char, 0), count)
        for char in u_letters:
            if char not in unused_letters:
                unused_letters.append(char)

        guess_letters = ", ".join(char for char in last_guess.upper())
        letter_colors= ", ".join(get_color(current_response))
        guess_explain = "; ".join(get_guess_explanation(last_guess, current_response,
            correct_letters=c_letters, letter_wrong_positions=l_w_positions, 
            appreance_counts=a_counts, unused_letters=u_letters))
        guess_template += guess_sum_last_v1.format(
            guess_word=last_guess.lower(),
            guess_letters=guess_letters,
            letter_colors=letter_colors,
            guess_explain=guess_explain
        )

        unk_positions = "; ".join(get_unk_position_explanation(
            correct_letters, letter_wrong_positions, appreance_counts))
        guess_template += guess_state_v1.format(
            num_guesses=attempts,
            correct_letters=correct_letters,
            unk_positions=unk_positions,
            unused_letters=', '.join(unused_letters)
        )

    guess_template += guess_analyze_v1.format(
        i=get_ordinal(attempts+1),
        next_word=current_guess
    )

    return guess_template.strip(), correct_letters, letter_wrong_positions, appreance_counts, unused_letters

import re
def split_fs_from_meta(meta: str):
    pos = meta.find("To help you better understand, ")
    new_meta = meta[:pos].strip()
    code_block_pattern = r"```.*?\n(.*?)```"
    code_blocks = re.findall(code_block_pattern, meta[pos:], re.DOTALL)
    fs_examples = []
    for code_block in code_blocks:
        user_input = code_block.split("# response")[0].split("# user input")[1].strip()
        response = code_block.split("# response")[1].strip()
        fs_examples.append((user_input, response))
    return new_meta, fs_examples