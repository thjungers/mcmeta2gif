"""
MCMETA2GIF

Convert an animated Minecraft texture (sprite PNG + MCMETA descriptor) to an animated GIF

Copyright (c) 2020 Thomas Jungers

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
import sys, os
from PIL import Image
from pprint import pprint
import numpy as np

TARGET_SIZE = 32
TIME_UNIT = 1000//20

def sprite2frames(filename):
    try:
        sprite = Image.open(filename)
        width = sprite.width
        height = sprite.height
        num_frames = height//width
        frames = []

        for i in range(0, num_frames):
            frame = sprite.crop((0, width*i, width, width*(i+1)))
            frame = frame.resize((TARGET_SIZE, TARGET_SIZE), Image.NEAREST)
            frames.append(frame)
        return frames

    except FileNotFoundError:
        exit("{} not found".format(filename))

def set_transparency(frame): # move the transparency index from 255 to 0 (required by PIL)
    frame = frame.convert('P', palette=Image.ADAPTIVE)
    palette = frame.getpalette()
    frame = (np.array(frame) + 1) % 256 # put the transparent index at 0 and shift all the others
    frame = Image.fromarray(frame).convert('P')
    frame.putpalette(palette[-3:] + palette[:-3])
    return frame


if len(sys.argv) != 2:
    exit("Usage: {} path/to/sprite.png".format(sys.argv[0]))

try:
    with open(sys.argv[1] + '.mcmeta', 'r') as mcmeta_file:
        mcmeta = json.load(mcmeta_file)
        interpolate = mcmeta['animation']['interpolate']
        frametime = mcmeta['animation']['frametime'] # number of time units per frame
        frame_order = mcmeta['animation']['frames']
        frame_settings = None
        for i in range(0, len(frame_order)):
            if type(frame_order[i]) is dict:
                frame_settings = frame_order.pop(i)
        
        sprite_frames = sprite2frames(sys.argv[1])

        frames = []
        duration = []

        for frame_num, next_frame_num, index in zip(frame_order, frame_order[1:] + frame_order[0:], range(0, len(frame_order))):
            if interpolate:
                for i in range(0, frametime):
                    frame = Image.blend(
                        sprite_frames[frame_num], 
                        sprite_frames[next_frame_num],
                        alpha=i/frametime
                    )
                    
                    frame = set_transparency(frame)

                    frames.append(frame)
                    duration.append(TIME_UNIT if (frame_settings is None or frame_settings['index'] != index) else TIME_UNIT*frame_settings['time'])
            else:
                frame = set_transparency(sprite_frames[frame_num])
                frames.append(frame)
                duration.append(TIME_UNIT*frametime)

        out_img = frames[0]
        out_img.save(
            os.path.splitext(sys.argv[1])[0] + '.gif', 
            save_all=True, 
            append_images=frames[1:], 
            duration=duration,
            loop=0, 
            transparency=0,
            disposal=2
        )

except FileNotFoundError:
    exit("{} not found".format(sys.argv[1] + '.mcmeta'))

