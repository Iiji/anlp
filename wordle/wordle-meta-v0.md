Let's play the game of Wordle. Wordle is a word-guessing game where the objective is to identify a secret 5-letter word within 6 attempts. Each guess must be a valid 5-letter word. After each guess, feedback is provided in the form of colored tiles:

- **Green tile**: The letter is in the correct position.
- **Yellow tile**: The letter is in the word but in the wrong position.
- **Gray tile**: The letter is not in the word at all.

The goal is to use this feedback to deduce the secret word in the fewest guesses possible.

You will act as the **guesser**, and I will act as the **judge**. You should contain your guess at the end of your response, formatted as an individual line: `GUESS: {word}`. After your guess, I will provide the feedback for your guess in the form of an image displaying colored tiles corresponding to your guess. This process repeats until the correct word is guessed or six attempts have been made.

To help you better guess, here are some tips:

- **Letter Frequency and Initial Guesses:**
  - The letters **E**, **S**, **I**, **A**, **R**, **N**, **T**, and **O** have the highest frequencies in English words, each occurring in more than 6% of words.
  - To maximize information gain from your initial guess, include as many of these high-frequency letters as possible.
  - Consider starting with words like **CRANE**, **RAISE**, **STARE**, **SEORA**, or **AUDIO**.
- **Strategic Approach for Early and Late Guesses:**
  - Early Guesses (First 2-3 Attempts):
    - Focus on testing new letters to identify as many correct letters as possible.
    - Do not worry about placing confirmed letters in the word at their exact positions yet.
  - Later Guesses:
    - Strictly adhere to all known constraints from previous feedbacks to ensure each guess could potentially be the correct word by fitting all the feedback received so far.