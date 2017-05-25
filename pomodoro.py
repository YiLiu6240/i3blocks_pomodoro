#!/usr/bin/env python3

'''
A pomodoro timer for i3blocks.
'''

import os
import datetime
import subprocess

def format_seconds(seconds):
    '''
    Format seconds into "%M:%S".
    '''
    minutes = seconds // 60
    seconds = round(seconds - (minutes * 60))
    return '{:02d}:{:02d}'.format(minutes, seconds)

class Pomo:
    '''
    A pomodoro timer.
    '''

    def __init__(self):

        self.icon_run = '➤'
        self.icon_pause = 'Ⅱ'
        self.work_length = datetime.timedelta(seconds=25 * 60)
        self.shortbreak_length = datetime.timedelta(seconds=5 * 60)
        self.longbreak_length = datetime.timedelta(seconds=15 * 60)
        self.sprint_length = 4
        self.period_length = datetime.timedelta(seconds=0)

        self.status = "NOTHING"
        self.sprint_circle = 0
        self.started_time = datetime.datetime.now()
        self.elapsed_time = datetime.timedelta(seconds=0)
        self.is_paused = True
        self.period_ended = False
        self.delta = datetime.timedelta(seconds=0)

        self.status_file = '/tmp/pomodoro_blocklet_status'

        if not os.path.isfile(self.status_file):
            self.update_record()

    def load_record(self):
        '''
        Load profile record from status_file
        '''
        record = open(self.status_file, 'r')
        # TODO: avoid using eval, use JSON instead?
        profile = eval(record.read())
        self.status = profile['status']
        self.sprint_circle = profile['sprint_circle']
        self.started_time = profile['started_time']
        self.elapsed_time = profile['elapsed_time']
        self.is_paused = profile['is_paused']
        self.delta = profile['delta']

    def update_record(self):
        '''
        Update record
        '''
        # record the time delta between now and `started_time`
        if self.is_paused:
            self.delta = datetime.datetime.now() - self.started_time
        record = open(self.status_file, 'w')
        profile = {'status': self.status,
                   'sprint_circle': self.sprint_circle,
                   'started_time': self.started_time,
                   'elapsed_time': self.elapsed_time,
                   'is_paused': self.is_paused,
                   'delta': self.delta}
        record.write(str(profile))

    def toggle_pause_state(self):
        '''
        Toggle is_paused
        '''
        if self.is_paused:
            self.is_paused = False
        else:
            self.is_paused = True
        self.update_record()

    def prolong_1min(self):
        '''
        Increase started_time by 1 minute
        '''
        self.started_time += datetime.timedelta(seconds=60)
        self.update_record()

    def shorten_1min(self):
        '''
        Decrease started_time by 1 minute
        '''
        self.started_time -= datetime.timedelta(seconds=60)
        self.update_record()

    def reset(self):
        '''
        Remove status file, and unset i3blocks environment variable
        $BLOCK_BUTTON
        '''
        os.remove(self.status_file)
        subprocess.check_output(['bash', '-c',
                                 'unset BLOCK_BUTTON'])

    def start_period(self):
        '''
        Start current period
        '''
        if self.period_ended:
            self.started_time = datetime.datetime.now()
            self.calc_times()
            self.update_record()

    def next_period(self):
        '''
        If current period has ended, switch to the next period
        '''
        if self.period_ended:
            if self.status == 'WORK':
                if self.sprint_circle >= self.sprint_length:
                    self.status = 'LONGBREAK'
                else:
                    self.status = 'SHORTBREAK'
            elif self.status == 'SHORTBREAK':
                self.sprint_circle += 1
                self.status = 'WORK'
            elif self.status == 'LONGBREAK':
                self.sprint_circle = 1
                self.status = 'WORK'
            else:
                self.status = 'WORK'
                self.sprint_circle = 1
            self.start_period()

    def block_respond(self):
        '''
        Respond to mouse event:
        - Left button: toggle pause
        - Middle button: reset pomo to initial state
        - Right button: switch to next period (once current period ended)
        - Wheel up: shorten timer
        - Wheel down: prolong timer
        '''
        block_button = os.environ.get('BLOCK_BUTTON')
        if block_button == '1':
            self.toggle_pause_state()
        elif block_button == '2':
            self.reset()
        elif block_button == '3':
            self.next_period()
        elif block_button == '4':
            self.shorten_1min()
            self.calc_times()
        elif block_button == '5':
            self.prolong_1min()
            self.calc_times()

    def calc_times(self):
        '''
        Calculate elapsed_time, period_length, and period_ended.
        '''
        if not self.is_paused:
            self.elapsed_time = datetime.datetime.now() - self.started_time
        else:
            self.elapsed_time = self.delta
            self.started_time = datetime.datetime.now() - self.delta

        if self.status == 'WORK':
            self.period_length = self.work_length
        elif self.status == 'SHORTBREAK':
            self.period_length = self.shortbreak_length
        elif self.status == 'LONGBREAK':
            self.period_length = self.longbreak_length

        self.period_ended = (self.elapsed_time >= self.period_length)

    def state_icon(self):
        '''
        Return pause state icon
        '''
        if self.is_paused:
            return self.icon_pause
        else:
            return self.icon_run

    def output(self):
        '''
        Produce output
        '''
        status_label = self.status
        if self.status == 'WORK':
            status_label += str(self.sprint_circle)
        block_output = '{}: {} {}/{} '.format(
            status_label, self.state_icon(),
            format_seconds(self.elapsed_time.seconds),
            format_seconds(self.period_length.seconds))
        return block_output

def main():
    '''
    How it works:

    Create a pomodoro timer `my_pomo`.

    At init, `my_pomo` checks if there has been a pomo status file:
    if not, write `my_pomo`'s initial state into the status file.

    `my_pomo` loads the record and replace its state variables.

    For the duration of the script, `my_pomo` calculates the current
    `elapsed_time` based on `started_time`. Then `my_pomo` checks mouse event
    and responds. And finally we get the block output label.
    '''
    my_pomo = Pomo()
    my_pomo.load_record()
    my_pomo.calc_times()
    my_pomo.block_respond()
    block_output = my_pomo.output()

    print(block_output)
    print(block_output)


if __name__ == '__main__':
    main()
