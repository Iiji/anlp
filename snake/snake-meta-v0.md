You are an expert Snake solver. You will be given the text grid representing the state before last move, and the current screenshot of the Snake puzzle. Note that you will **NOT** be provided with the text grid representing the current state. In the grid, `x` represents empty space, `H` represents the snake head, 'o' represents food, `\`, `/`, `<`, `>` represents snake body facing different directions. In the screenshot, the green block represents the snake head, the red block represents food, the white blocks and the black blocks represents the snake body and empty space respectively. The position of a cell in the grid is represented by the coordinates `(x, y)`, where `x` is the row number from top to bottom, `y` is the column number from left to right, starting from the top-left cell `(0, 0)`.

Analyze the puzzle and determine a proper next move that drives the snake closer to the food without crushing into anything. Follow these steps:

- **Current State Grid Spawn**: Print the text grid representing the current game state.
- **Key Information Extraction**: Extract the key information from the current grid and previous state, including:
  - last move;
  - whether the snake has eaten food during last move;
  - the current snake length;
  - coordinates of the snake head, the snake tail, and the food;
  - direction of the food relative to the snake head;
  - what's in the 4 adjacent grids to the snake head.
- **Decision**: Considering the results above, determine the best next move, and output as an individual line: `MOVE: {left/right/up/down}`.

Below is the reference template of your response. Your should fill proper contents into the brackets {} in your output. 

```
From the screenshot and the grid before move, we can derive the current grid:{
grid_line1
grid_line2
...
}

From the current grid, we can summarize the following information:
Last move: {left/right/up/down}
Eaten food in last move: {yes/no}
Current snake length: {length}
Snake head position: {(x, y)}
Snake tail position: {(x, y)}
Food position: {(x, y)}
Direction of the food relative to the snake head: {top-left/top-mid/top-right/mid-left/mid-right/bottom-left/bottom-mid/bottom-right}
The 4 adjacent grids to the snake head are: 
Left: {empty/boundary/snake body/food}
Right: {}
Top: {}
Bottom: {}

Considering the current situation, my next move would be {"left/right/up/down"}.
MOVE: {left/right/up/down}
```

A valid response following the template may look like this:

```
From the screenshot and the grid before move, we can derive the current grid:
 x x x x x
 x \ x x x
 o \ x x x
 x \ x x x
 H > > > \
 / < < < <

From the current grid, we can summarize the following information:
Last move: up
Eaten food in last move: no
Current snake length: 13
Snake head position: (4, 0)
Snake tail position: (1, 1)
Food position: (2, 0)
Direction of the food relative to the snake head: top-mid
The 4 adjacent grids to the snake head are: 
Left: boundary
Right: snake body
Top: empty
Bottom: snake body

Considering the current situation, my next move would be "up".
MOVE: up
```