# Notes — prompts


## 1

> Firstly create a notes.md file and collect all my prompts in it. Build the Cassino card game. There is a tests/test_casino.py file that defines the rules. Please write the game logic so that the uv run pytest command passes without any errors. You must not edit or modify the tests/test_casino.py file under any circumstances. Once all tests pass, please build a web interface where I can play a whole deal against the computer, and tell me the exact command I need to use to start the table in the browser.

## 2

> please also add a game tutorial

## 3

> When I open the game interface and try to make a move, I get multiple 'Illegal move: Failed to fetch' errors in the log. I cannot play the game.

## 4

> where should I type uv run python server.py

## 5

> [screenshot of a PowerShell window showing: `uv : The term 'uv' is not recognized as the name of a cmdlet, function, script file, or operable program...`] what should I do?

## 6

> [screenshot of a PowerShell window showing a venv activation command followed by `uv run python server.py` successfully printing "Cassino is running at http://127.0.0.1:8000/"] what should I do next?

## 7

> I found a major bug in the game logic while playing. The game log says: 'The computer played AC, QD and captured 10S, 3D'. This is an illegal move. In Cassino, a player or the computer can only play exactly ONE card from their hand per turn. The computer played two cards at once. Please fix the computer's logic so it strictly plays only one card per turn. Also ensure the capture logic is mathematically correct.

## 8

> Bug: The game does not recognize 'Building'. I selected a 4 from my hand and a 2 on the table (while holding a 6), but the Play button remained disabled. Please fix the frontend logic to allow building.

## 9

(Sent after rejecting an AskUserQuestion prompt about whether to implement building.)

> You are absolutely right. Since tests/test_casino.py does not test the 'Building' mechanic, we should not implement it to avoid breaking the existing tests. Let's keep the game simple: just placing and capturing. Please just ensure the game logic allows me to simply trail (place) a card. If I select exactly ONE card from my hand and ZERO cards from the table, the 'Play' button should be active and allow me to place it

## 10

> It seems to me that the one card per turn problem is still valid. check it and fix it

## 11

> I found two major bugs in the game log. First: 'The computer played QD and captured 4S, 8S'. In standard Cassino, face cards (J, Q, K) have no numerical value and can ONLY capture matching face cards (e.g., a Queen can only capture another Queen). Please fix the logic so face cards cannot capture sums. Second: The log shows I made two moves in a row without the computer playing in between ('You placed AH...' immediately followed by 'You played 2S...'). The turn order broke. Please fix the turn logic so players strictly alternate.


## 13

> make it visually better. Instead of the english name of the cards use the exact simbol and number which appears on the cards.

## 14

> Please explain the value of the cards with figures (J, D, K, A)  and add this to the How to play section

## 15

> I think I'm ready, the game works just as I like it. What is the next step? What shoul dI do with the test?

## 16

> I should submit these: What your fork must contain
> What
> uv run pytest	Passes — with tests/test_casino.py exactly as you got it.
> README.md	One command that starts the table in the browser.
> NOTES.md	What playing found, and what you asked the agent to change.
> Have I got all of these? If not please create it.

FINDINGS
>tóhe game log showed the computer playing two cards from its hand at the same time (e.g., "The computer played AC, QD and captured 10S, 3D").

Action taken: Instructed the AI to fix the backend logic to strictly enforce the Cassino rule: exactly ONE card can be played per turn. The AI fixed this, and after a server restart, the computer only played one card per turn.

> When trying to simply place (trail) a card on the table without capturing anything (selecting exactly one hand card and zero table cards), the 'Play' button remained disabled with the message: "That selection doesn't add up to a legal move yet."

Action taken: Asked the AI to fix the frontend validation logic. The AI updated the frontend so the 'Play' button becomes active when trailing a single card, allowing the game to proceed when no captures are possible.

>Tried to perform a "Build" move (selecting a 4 from hand and a 2 on the table while holding a 6). The frontend rejected it.

AI Interaction: The AI correctly pointed out that the provided tests/test_casino.py suite only tests for placing and direct/sum capturing. It does not support or test the concept of "Building" or leaving grouped cards on the table.

Resolution: Decided not to implement the Building mechanic.

>Cannot trail a card. The Play button is disabled when selecting only one card from the hand and none from the table. Asked AI to fix frontend validation.

> Noticed the game allowed me to make two consecutive moves ("You placed AH..." immediately followed by "You played 2S..."). I initially flagged this as a turn-order bug.

AI Interaction: The AI analyzed tests/test_casino.py and pointed out that this is an intentional rule required by the test test_sweep_and_the_double_move_after_it. Placing a card onto an empty table after a sweep does not pass the turn.

>Thought I found a turn-order bug (two consecutive moves), but the AI correctly pointed out that test_casino.py explicitly requires a 'free move' after a sweep (test_sweep_and_the_double_move_after_it). Decided to keep the logic as tested.
>Noticed in the game log that the computer used a Queen to capture numbered cards by sum ("The computer played QD and captured 4S, 8S").

Action taken: In standard Cassino, face cards (J, Q, K) have no numerical value and can only capture matching face cards. Prompted the AI to fix the backend capturing logic to prevent face cards from treating sums (e.g., 4+8=12) as valid captures, while ensuring tests still pass.


