# This is a simpler version of https://github.com/m-lundberg/simple-pid/blob/master/simple_pid/pid.py#L198
# It has been adjusted for the raspberry pi pico
import time


def _clamp(value, limits):
    lower, upper = limits
    if value is None:
        return None
    elif (upper is not None) and (value > upper):
        return upper
    elif (lower is not None) and (value < lower):
        return lower
    return value


class PID(object):
    """A simple PID controller."""

    def __init__(
            self,
            Kp=1.0,
            Ki=0.0,
            Kd=0.0,
            set_point=0,
            output_limits=(None, None),
            starting_output=0.0
    ):
        """
        Initialize a new PID controller.

        :param Kp: The value for the proportional gain Kp
        :param Ki: The value for the integral gain Ki
        :param Kd: The value for the derivative gain Kd
        :param set_point: The initial set-point that the PID will try to achieve
        :param output_limits: The initial output limits to use, given as an iterable with 2
            elements, for example: (lower, upper). The output will never go below the lower limit
            or above the upper limit. Either of the limits can also be set to None to have no limit
            in that direction. Setting output limits also avoids integral windup, since the
            integral term will never be allowed to grow outside the limits.
        :param starting_output: The starting point for the PID's output. If you start controlling
            a system that is already at the set-point, you can set this to your best guess at what
            output the PID should give when first calling it to avoid the PID outputting zero and
            moving the system away from the set-point.
        """
        self.Kp, self.Ki, self.Kd = Kp, Ki, Kd
        self.set_point = set_point

        self._min_output, self._max_output = None, None

        self._proportional = 0
        self._integral = 0
        self._derivative = 0

        self._last_time = time.ticks_us()
        self._last_error = 0

        self.output_limits = output_limits

        # Set initial state of the controller
        self._integral = _clamp(starting_output, output_limits)

    def __call__(self, input_):
        """
        Update the PID controller.

        Call the PID controller with *input_* and calculate and return a control output if
        sample_time seconds has passed since the last update. If no new output is calculated,
        return the previous output instead (or None if no value has been calculated yet).
        """
        now = time.ticks_us()
        dt = (now - self._last_time)*1e-6

        # Compute error terms
        error = self.set_point - input_
        d_error = error - self._last_error

        # todo: make this avoid integral windup
        self._proportional = self.Kp*error
        self._integral += self.Ki*error*dt
        self._derivative = self.Kd*d_error/dt

        self._integral = _clamp(self._integral, self.output_limits)

        # Compute final output
        output = self._proportional + self._integral + self._derivative
        output = _clamp(output, self.output_limits)

        # Keep track of state
        self._last_error = error
        self._last_time = now

        return output

    def __repr__(self):
        return (
            '{self.__class__.__name__}('
            'Kp={self.Kp!r}, Ki={self.Ki!r}, Kd={self.Kd!r}, '
            'set_point={self.set_point!r}, output_limits={self.output_limits!r}'
            ')'
        ).format(self=self)

    @property
    def components(self):
        """
        The P-, I- and D-terms from the last computation as separate components as a tuple. Useful
        for visualizing what the controller is doing or when tuning hard-to-tune systems.
        """
        return self._proportional, self._integral, self._derivative

    @property
    def tunings(self):
        """The tunings used by the controller as a tuple: (Kp, Ki, Kd)."""
        return self.Kp, self.Ki, self.Kd

    @tunings.setter
    def tunings(self, tunings):
        """Set the PID tunings."""
        self.Kp, self.Ki, self.Kd = tunings

    @property
    def output_limits(self):
        """
        The current output limits as a 2-tuple: (lower, upper).

        See also the *output_limits* parameter in :meth:`PID.__init__`.
        """
        return self._min_output, self._max_output

    @output_limits.setter
    def output_limits(self, limits):
        """Set the output limits."""
        if limits is None:
            self._min_output, self._max_output = None, None
            return

        min_output, max_output = limits

        if (None not in limits) and (max_output < min_output):
            raise ValueError('lower limit must be less than upper limit')

        self._min_output = min_output
        self._max_output = max_output

        self._integral = _clamp(self._integral, self.output_limits)

    def reset(self):
        """
        Reset the PID controller internals.

        This sets each term to 0 as well as clearing the integral, the last output and the last
        input (derivative calculation).
        """
        self._proportional = 0
        self._integral = 0
        self._derivative = 0

        self._integral = _clamp(self._integral, self.output_limits)

        self._last_time = time.ticks_us()
