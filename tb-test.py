from WF_SDK import device, scope, wavegen, tools, error  # import instruments

import matplotlib.pyplot as plt  # needed for plotting
from time import sleep  # needed for delays

"""-----------------------------------------------------------------------"""

v_write = 0.3
v_read = 1
v_now = v_read

try:
    # connect to the device
    device_data = device.open()

    """-----------------------------------"""

    # handle devices without analog I/O channels
    if device_data.name != "Digital Discovery":

        # initialize the scope with default settings
        scope.open(device_data)

        # set up triggering on scope channel 1
        scope.trigger(device_data, enable=True, source=scope.trigger_source.analog, channel=1, level=v_now/2)

        # generate a pulse on channel 1
        wavegen.generate(device_data, channel=1, function=wavegen.function.pulse, offset=0, frequency=10e03, amplitude=v_now, repeat=1)

        # record data with the scopeon channel 1
        buffer = scope.record(device_data, channel=1)

        # limit displayed data size
        # length = len(buffer)
        # if length > 10000:
        #     length = 10000
        # buffer = buffer[0:length]

        # generate buffer for time moments
        time = []
        for index in range(len(buffer)):
            time.append(index * 1e03 / scope.data.sampling_frequency)  # convert time to ms

        # plot
        plt.plot(time, buffer)
        plt.xlabel("time [ms]")
        plt.ylabel("voltage [V]")
        plt.show()

        # reset the scope
        scope.close(device_data)

        # reset the wavegen
        wavegen.close(device_data)

    """-----------------------------------"""

    # close the connection
    device.close(device_data)

except error as e:
    print(e)
    # close the connection
    device.close(device.data)