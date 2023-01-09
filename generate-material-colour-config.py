#!/usr/bin/env python3

# https://github.com/avanishsubbiah/material-color-utilities-python
from material_color_utilities_python import *

def generate_config(scheme, program):
    output = f'\n{program}:\n--\n\n'
    for role, colour in scheme.props.items():
        if program == 'i3wm':
            output += f'set $md_sys_color_{role} {hexFromArgb(colour)}\n'
        elif program == 'polybar':
            output += f'md_sys_color_{role} = {hexFromArgb(colour)}\n'
    output += '\n--\n'
    return output

print('Source colour: [#4285f4]')
source_colour = input('> ')
source_colour = '#4285f4' if len(source_colour) != 7 else source_colour
print('Scheme: [light]/dark ')
user_scheme = input('> ')
user_scheme = 'light' if user_scheme not in ('light', 'dark') else user_scheme

theme = themeFromSourceColor(argbFromHex(source_colour))
scheme = theme['schemes'][user_scheme]

print(f'Generated config for {user_scheme} scheme based on colour {source_colour}:')
print(generate_config(scheme, 'i3wm'))
print(generate_config(scheme, 'polybar'))
