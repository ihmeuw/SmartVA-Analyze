from progressbar import Timer


class AdaptiveETA(Timer):
    """
    NOTE: This code was inspired by the python-progressbar Google Code repo
    because it does not exist in the pypi repo.
    https://code.google.com/p/python-progressbar/
    """

    TIME_SENSITIVE = True
    NUM_SAMPLES = 10

    def __init__(self, format_='Elapsed Time: %s'):
        super(AdaptiveETA, self).__init__(format_)
        self._last_val = 0

    def _update_samples(self, elapsed, val_delta=1):
        if not hasattr(self, 'samples'):
            self.samples = [elapsed]
            self._last_elapsed = elapsed
        else:
            self.samples.extend([(elapsed - self._last_elapsed) / val_delta] * val_delta)
            self._last_elapsed = elapsed
        self.samples = self.samples[-self.NUM_SAMPLES:]
        return sum(self.samples) / len(self.samples)

    def update(self, pbar):
        if pbar.currval == 0:
            self.NUM_SAMPLES = int(pbar.maxval * 0.25) + 1
            self._update_samples(pbar.seconds_elapsed)
            self._last_val = pbar.currval
            return '--:--:--'
        elif pbar.finished:
            return 'Time: {:s}'.format(self.format_time(pbar.seconds_elapsed))
        else:
            sample_avg = self._update_samples(pbar.seconds_elapsed, abs(pbar.currval - self._last_val))
            eta = (pbar.maxval * sample_avg) - (pbar.currval * sample_avg)
            self._last_val = pbar.currval
            return 'ETA:  {:s}'.format(self.format_time(eta))
