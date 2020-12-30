# mcmeta2gif
Convert an animated Minecraft texture (sprite PNG + MCMETA descriptor) to an animated GIF

## Usage
python mcmeta2gif.py path/to/texture.png

Requires a texture.png.mcmeta within the same folder, containing at least a 'animation' dictionary (full description: see https://minecraft.gamepedia.com/Resource_Pack#Animation).

Editable parameters:
* TARGET_SIZE: the output gif is a square of TARGET_SIZE × TARGET_SIZE pixels
* TIME_UNIT: the time per frame in milliseconds for the output gif

## Requirements
* Python 3
* PIL
* numpy
