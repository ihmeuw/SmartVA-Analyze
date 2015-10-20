from progressbar import Timer


class AdaptiveETA(Timer):
    """
    NOTE: This code was inspired by the python-progressbar Google Code repo
    because it does not exist in the pypi repo.
    https://code.google.com/p/python-progressbar/
    """

    TIME_SENSITIVE = True
    NUM_SAMPLES = 10

    def _update_samples(self, elapsed):
        # TODO - This only really works if the updates come in sequentially.
        if not hasattr(self, 'samples'):
            self.time_sample = elapsed
            self.samples = [elapsed]  # * (self.NUM_SAMPLES + 1)
        else:
            self.samples.append(elapsed - self.time_sample)
            self.time_sample = elapsed
        if len(self.samples) > self.NUM_SAMPLES:
            self.samples.pop(0)
        return sum(self.samples) / len(self.samples)

    def update(self, pbar):
        if pbar.currval == 0:
            self.NUM_SAMPLES = int(pbar.maxval * 0.25) + 1
            self._update_samples(pbar.seconds_elapsed)
            return '--:--:--'
        elif pbar.finished:
            return 'Time: {:s}'.format(self.format_time(pbar.seconds_elapsed))
        else:
            sample_avg = self._update_samples(pbar.seconds_elapsed)
            eta = (pbar.maxval * sample_avg) - (pbar.currval * sample_avg)
            return 'ETA:  {:s}'.format(self.format_time(eta))


class AdaptiveETA2(Timer):
    """Widget which attempts to estimate the time of arrival.

    Uses a weighted average of two estimates:
      1) ETA based on the total progress and time elapsed so far
      2) ETA based on the progress as per tha last 10 update reports

    The weight depends on the current progress so that to begin with the
    total progress is used and at the end only the most recent progress is
    used.

    NOTE: This code was borrowed from the python-progressbar Google Code repo
    because it does not exist in the pypi repo.
    https://code.google.com/p/python-progressbar/
    """

    TIME_SENSITIVE = True
    NUM_SAMPLES = 10

    def _update_samples(self, currval, elapsed):
        sample = (currval, elapsed)
        if not hasattr(self, 'samples'):
            self.samples = [sample] * (self.NUM_SAMPLES + 1)
        else:
            self.samples.append(sample)
        return self.samples.pop(0)

    def _eta(self, maxval, currval, elapsed):
        return elapsed * maxval / float(currval) - elapsed

    def update(self, pbar):
        """Updates the widget to show the ETA or total time when finished."""
        if pbar.currval == 0:
            return 'ETA:  --:--:--'
        elif pbar.finished:
            return 'Time: %s' % self.format_time(pbar.seconds_elapsed)
        else:
            elapsed = pbar.seconds_elapsed
            currval1, elapsed1 = self._update_samples(pbar.currval, elapsed)
            eta = self._eta(pbar.maxval, pbar.currval, elapsed)
            if pbar.currval > currval1:
                etasamp = self._eta(pbar.maxval - currval1,
                                    pbar.currval - currval1,
                                    elapsed - elapsed1)
                weight = (pbar.currval / float(pbar.maxval)) ** 0.5
                eta = (1 - weight) * eta + weight * etasamp
            return 'ETA:  %s' % self.format_time(eta)