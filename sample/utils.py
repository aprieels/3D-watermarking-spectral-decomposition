import sys

def progress(count, total, prefix=''):
    bar_length = 50
    filled_len = int(round(bar_length * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '#' * filled_len + '-' * (bar_length - filled_len)

    #sys.stdout.write('%s [%s] %s%s | %s/%s\r' % (prefix, bar, percents, '%', count, total))
    #sys.stdout.flush()