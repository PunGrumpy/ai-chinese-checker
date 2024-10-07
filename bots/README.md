# 🤖 Custom Bot Guide for Chinese Checkers

Do you think the default bots are too easy to beat? 🎯 You can create your own bots to challenge them or even battle against yourself! Here's how you can get started.

## 📁 Getting Started

1. **Copy the template**: First, make a copy of `CustomBotTemplate.py` and save it in the same folder (`custom_bots`).
2. **Rename the bot**: Rename the filename and class name to something meaningful. It's a good practice to make the filename match the class name.

Now you're ready to explore how to make your bot smarter!

## 📐 Coordinate System

Thanks to [Red Blob Games](https://www.redblobgames.com/grids/hexagons/) for the hexagonal grid guide!

In Chinese Checkers, the board is a hexagonal grid with three axes and six directions. However, we simplify this to a 2D coordinate system. The axes are drawn on the game board like this:

![Coordinate System 2](/images/coor2.png)

Here’s a quick cheat sheet for the six directions:

![Coordinate System 1](/images/coor1.png)

And here are all the coordinates on the board:

![All Coordinates](/images/all_coors.jpg)

Coordinates are stored as `tuple(int, int)` in the code. You can manipulate them using the following functions from `game_logic.helpers`:

| ⚙️ Function         | 📜 Description                                   |
| ------------------- | ------------------------------------------------ |
| `add(tuple, tuple)` | Adds two coordinates together.                   |
| `mult(tuple, int)`  | Multiplies a coordinate by an integer (scaling). |

To move your bot, you return a pair of start and end coordinates like this:

```py
return [subj_to_obj_coor(start, self.playerNum), subj_to_obj_coor(end, self.playerNum)]
```

## 🛠️ Useful Functions

Here are some helpful functions from `game_logic.game` to assist in creating your bot’s logic:

| 🛠️ Function           | 📊 Data Type                                | 📜 Description                                                                                                |
| --------------------- | ------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `allMovesDict()`      | `dict(tuple(int,int):list(tuple(int,int)))` | Returns all valid moves for your pieces. Key: piece coordinate, Value: list of valid destination coordinates. |
| `getBoardState()`     | `dict(tuple(int,int):int)`                  | Returns the board state. Key: coordinates, Value: player number or 0 (vacant).                                |
| `getBoolBoardState()` | `dict(tuple(int,int):bool)`                 | Similar to `getBoardState()`, but with `True` (occupied) and `False` (vacant).                                |

Remember to convert the coordinates using `subj_to_obj_coor()` when returning a move, as shown in the template.

## 🔢 Constants

Here are some constants from `game_logic.literals` that you might find useful:

| 🔢 Constant    | 📊 Data Type                    | 📜 Description                                                                                      |
| -------------- | ------------------------------- | --------------------------------------------------------------------------------------------------- |
| `START_COOR`   | `dict(int:set(tuple(int,int)))` | Starting coordinates for each player. Key: `playerNum`, Value: set of starting positions.           |
| `END_COOR`     | `dict(int:set(tuple(int,int)))` | End (goal) coordinates for each player.                                                             |
| `NEUTRAL_COOR` | `set(tuple(int,int))`           | Coordinates of neutral spaces on the board.                                                         |
| `ALL_COOR`     | `set(tuple(int,int))`           | Set of all valid board coordinates.                                                                 |
| `DIRECTIONS`   | `set(tuple(int,int))`           | Unit vectors for the six directions on the board. `{(1,0), (0,1), (-1,1), (-1,0), (0,-1), (1,-1)}`. |

---

Start experimenting with these functions to make your custom bot the smartest on the board! 🧠🎮
