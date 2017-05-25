# i3blocks_pomodoro

Yet another pomodoro timer, but this is a blocklet for i3blocks.

A python rewrite of the original bash version by [slaxor](https://github.com/slaxor/pomodoro_blocklet). I added a pause toggle to the timer.

Changes:
- A python oop rewrite.
- Added option to toggle pause.
- Slightly adjusted the output format.

# Installation

Add a blocklet to i3blocks settings, and change `path/to/pomodoro.py` to where you like.

```ini
[pomodoro]
label=🕒
command=path/to/pomodoro.py
interval=1
```
# Usage

- Left button: toggle pause.
- Middle button: reset.
- Right button: switch to next period, once the elapsed time passes the period time length.
- Wheel up: shorten timer by 1 minute.
- Wheel down: prolong timer by 1 minute.
