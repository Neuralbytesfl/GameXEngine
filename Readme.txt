FPS GAME AND MAP EDITOR
========================

Author: Jose Ayala

Overview:
---------
This project includes two components:

1. **FPS Game (fps_game.py):** 
   - A first-person shooter game with raycasting for wall rendering and player movement.
   - Features:
     - Help toggle (F1)
     - Fetch message from Ollama (F2)
     - Fullscreen/windowed mode toggle (F)

2. **Map Editor (map_editor.py):** 
   - A tool for creating and editing maps for the FPS game.
   - Features:
     - Place walls and set starting positions
     - Save maps to 'map.txt' and load maps from 'map.txt'

Installation:
-------------
1. Install Python 3.x and the required libraries:

Usage:
------
- **FPS Game:** Run `fps_game.py` to start the game.
- **Map Editor:** Run `map_editor.py` to create or modify maps.

Controls:
---------
- **FPS Game:**
- W, A, S, D: Move
- Mouse: Look Around
- F1: Toggle Help
- F2: Fetch Ollama Message
- F: Toggle Fullscreen/Windowed Mode

- **Map Editor:**
- Left Click: Toggle walls and open spaces
- 'S': Set/Move Starting Position
- Save Button: Save the current map
- Load Button: Load a previously saved map

License:
--------
MIT License

For more details or questions, contact Jose Ayala.
