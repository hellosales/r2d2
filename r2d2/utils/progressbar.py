import os
import sys
import fcntl
import struct
import termios
import datetime
from string import Template
from django.conf import settings
from django.template.defaultfilters import filesizeformat
from django.utils.termcolors import colorize
from r2d2.utils.backports import get_total_seconds


class ProgressBarError(Exception):
    pass


class AlreadyFinishedError(ProgressBarError):
    pass


def get_terminal_width():
    try:
        width = struct.unpack('hh',
            fcntl.ioctl(0, termios.TIOCGWINSZ, '1234'))[1]
    except (IndexError, IOError):
        width = None
    return width


class ProgressBar(object):

    default_elements = ['percentage', 'bar', 'steps', 'eta', 'time']

    def __init__(self, steps=100, stream=None, elements=None, sequence=None,
        width=20):
        self.step = 0
        self.steps = steps
        self.stream = stream or sys.stderr
        self.bar_char = '='
        self.width = width
        self.separator = ' | '
        self.elements = elements or self.default_elements
        self.started = None
        self.finished = False
        self.steps_label = 'Step'
        self.time_label = 'Time'
        self.eta_label = 'ETA'
        self.speed_label = 'Speed'
        self.transfer_label = 'Transfer'
        self.last_percentage_done = -1
        self.hide_output_if_not_isatty = True

        self.transfer_template = '{label}: {done} / {total}'

        self.sequence = sequence
        if self.sequence:
            try:
                self.steps = len(sequence)
            except TypeError:
                pass

        if hasattr(self.stream, 'fileno'):
            self.isatty = os.isatty(self.stream.fileno())
        else:
            self.isatty = False

    def __str__(self):
        line = self.get_line()
        width = get_terminal_width()
        if width:
            line = line.ljust(width, ' ')
        return line

    def __iter__(self):
        start = self.step
        end = self.steps + 1
        for x in xrange(start, end):
            self.render(x)
            yield x

    def iterobjects(self):
        if self.sequence:
            iterator = iter(self.sequence)
            for x in self:
                yield iterator.next()

    def get_separator(self):
        return self.separator

    def get_bar_char(self):
        return self.bar_char

    def get_bar(self):
        char = self.get_bar_char()
        perc = self.get_percentage()
        length = int(self.width * perc / 100)
        if length > self.width:
            length = self.width
        bar = char * length
        bar = bar.ljust(self.width)
        return bar

    def get_elements(self):
        return self.elements

    def get_template(self):
        separator = self.get_separator()
        elements = self.get_elements()
        return Template(separator.join((('$%s' % e) for e in elements)))

    def get_total_time(self, current_time=None):
        if current_time is None:
            current_time = datetime.datetime.now()
        if not self.started:
            return datetime.timedelta()
        return current_time - self.started

    def get_rendered_total_time(self):
        delta = self.get_total_time()
        if not delta:
            ttime = '-'
        else:
            ttime = str(delta)
        return '%s %s' % (self.time_label, ttime)

    def get_eta(self, current_time=None):
        if current_time is None:
            current_time = datetime.datetime.now()
        if self.step == 0:
            return datetime.timedelta()
        total_seconds = get_total_seconds(self.get_total_time())
        eta_seconds = total_seconds * self.steps / self.step - total_seconds
        return datetime.timedelta(seconds=int(eta_seconds))

    def get_rendered_eta(self):
        eta = self.get_eta()
        if not eta:
            eta = '--:--:--'
        else:
            eta = str(eta).rjust(8)
        return '%s: %s' % (self.eta_label, eta)

    def get_percentage(self):
        if not self.steps:
            return 0.0
        return float(self.step) / self.steps * 100

    def get_rendered_percentage(self):
        perc = self.get_percentage()
        return ('%s%%' % (int(perc))).rjust(5)

    def get_rendered_steps(self):
        return '%s: %s/%s' % (self.steps_label, self.step, self.steps)

    def get_rendered_speed(self, step=None, total_seconds=None):
        if step is None:
            step = self.step
        if total_seconds is None:
            total_seconds = get_total_seconds(self.get_total_time())
        if step <= 0 or total_seconds <= 0:
            speed = '-'
        else:
            speed = filesizeformat(float(step) / total_seconds)
        return '%s: %s/s' % (self.speed_label, speed)

    def get_rendered_transfer(self, step=None, steps=None):
        if step is None:
            step = self.step
        if steps is None:
            steps = self.steps

        if steps <= 0:
            return '%s: -' % self.transfer_label
        total = filesizeformat(float(steps))
        if step <= 0:
            transferred = '-'
        else:
            transferred = filesizeformat(float(step))
        return self.transfer_template.format(label=self.transfer_label,
            done=transferred, total=total)

    def get_rendered_whirl(self):
        chars = '-/|\\*'
        if self.step >= self.steps:
            return '*'
        return chars[self.step % len(chars)]

    def get_context(self):
        return {
            'percentage': self.get_rendered_percentage(),
            'bar': self.get_bar(),
            'steps': self.get_rendered_steps(),
            'time': self.get_rendered_total_time(),
            'eta': self.get_rendered_eta(),
            'speed': self.get_rendered_speed(),
            'transfer': self.get_rendered_transfer(),
            'whirl': self.get_rendered_whirl(),
        }

    def get_line(self):
        template = self.get_template()
        context = self.get_context()
        return template.safe_substitute(**context)

    def write(self, data):
        self.stream.write(data)

    def get_rendered(self, step, finish=True, return_prefix=True,
            write_new_line_if_finish=True):
        line = None
        if not self.started:
            self.started = datetime.datetime.now()
        if self.finished:
            raise AlreadyFinishedError
        self.step = step
        if not settings.TESTING:
            line = str(self)
            if self.isatty:
                if return_prefix:
                    self.write('\r')
                self.write(line)
            elif (not self.hide_output_if_not_isatty and
                self.get_percentage() - self.last_percentage_done >= 1):
                self.write('%s\n' % line)
        self.last_percentage_done = int(self.get_percentage())
        if finish and step == self.steps:
            self.finished = True
            if write_new_line_if_finish:
                self.write('\n')
        return line

    def render(self, step, finish=True):
        self.get_rendered(step, finish)

    def update(self, step, steps=None):
        if steps:
            self.steps = steps
            if steps > step:
                self.finished = False
        self.render(step, finish=False)


class ColoredProgressBar(ProgressBar):

    BAR_COLORS = (
        (10, 'red'),
        (30, 'magenta'),
        (50, 'yellow'),
        (99, 'green'),
        (100, 'blue'),
    )

    def __init__(self, *args, **kwargs):
        if 'color' in kwargs:
            color = kwargs.pop('color')
            self.BAR_COLORS = [(100, color)]
        super(ColoredProgressBar, self).__init__(*args, **kwargs)

    def get_line(self):
        line = super(ColoredProgressBar, self).get_line()
        perc = self.get_percentage()
        if perc > 100:
            color = 'blue'
        for max_perc, color in self.BAR_COLORS:
            if perc <= max_perc:
                break
        return colorize(line, fg=color)


class AnimatedProgressBar(ProgressBar):

    def get_bar_char(self):
        chars = '-/|\\'
        if self.step >= self.steps:
            return '='
        return chars[self.step % len(chars)]


class MultipleProgressBar(object):

    def __init__(self, *bars):
        self.bars = bars

    def render(self, *values):
        """
        Renders all bars - number of values should be same as number of bars.
        """
        stream = self.bars[0].stream
        stream.write('\r')
        lines = []
        for value, bar in zip(values, self.bars):
            bar.step = value
            lines.append(bar.get_line())
        line = ' '.join(lines)
        width = get_terminal_width()
        if width:
            line = line.ljust(width, ' ')
        stream.write(line)


class ProgressWhirl(ProgressBar):
    default_elements = ['whirl']


def main():
    import time

    print "Standard progress bar..."
    bar = ProgressBar(30)
    for x in xrange(1, 31):
            bar.render(x)
            time.sleep(0.02)
    bar.stream.write('\n')
    print

    print "Multiple progress bars..."
    bar1 = ColoredProgressBar(20, color='green')
    bar1.width = 15
    bar1.steps_label = 'Files'

    bar2 = ColoredProgressBar(100, color='blue')
    bar2.width = 15
    bar2.steps_label = 'Sites'

    bar1.elements = bar2.elements = ['bar', 'steps']

    mbar = MultipleProgressBar(bar1, bar2)
    for x in xrange(1, 21):
        mbar.render(x, x * 2)
        time.sleep(0.05)
    print
    print

    print "Empty bar..."
    bar = ProgressBar(50)
    bar.render(0)
    print
    print

    print "Colored bar..."
    bar = ColoredProgressBar(20)
    for x in range(bar.steps + 1):
        bar.update(x)
        time.sleep(0.01)
    print

    print "Animated char bar..."
    bar = AnimatedProgressBar(20)
    for x in bar:
        time.sleep(0.1)
    print

    print "File transfer bar, breaks after 2 seconds ..."
    total_bytes = 1024 * 1024 * 2
    bar = ProgressBar(total_bytes)
    bar.width = 30
    bar.elements = ['percentage', 'bar', 'transfer', 'time', 'eta', 'speed']
    for x in xrange(0, bar.steps, 1024):
        bar.render(x)
        time.sleep(0.01)
        now = datetime.datetime.now()
        if now - bar.started >= datetime.timedelta(seconds=2):
            bar.render(x + 1)
            break
    print
    print

    print "ProgressWhirl"
    whirl = ProgressWhirl(40)
    whirl.elements += ['steps', 'percentage']
    for x in range(whirl.steps + 1):
        whirl.update(x)
        time.sleep(0.05)
    print
    print

    print "Standard progress bar (no terminal simulation) ..."
    bar = ProgressBar(20)
    bar.isatty = False
    for x in xrange(1, bar.steps + 1):
        bar.render(x)
        time.sleep(0.01)
    bar.stream.write('\n')
    print

if __name__ == '__main__':
    main()

