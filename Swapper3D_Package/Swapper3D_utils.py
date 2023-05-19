# Octoprint plugin name: Swapper3D, File: Swapper3D_utils.py, Author: BigBrain3D, License: AGPLv3
 
# Import required libraries
import serial
import serial.tools.list_ports
import time

def parity_of(int_type):
    """
    Function to calculate parity bit for a given integer.

    :param int_type: Integer value to calculate parity for
    :return: Parity bit (0 or 1)
    """
    parity = 0
    while (int_type):
        parity = ~parity
        int_type = int_type & (int_type - 1)
    return parity

def try_handshake(plugin):
    """
    Function to handle serial communication handshake with the Swapper3D device.

    :param plugin: The Swapper3D OctoPrint plugin instance
    :return: The serial connection object if the handshake is successful, None and an error message otherwise
    """
    # Automatically detect Arduino Uno or other serial ports
    arduino_ports = [port.device for port in serial.tools.list_ports.comports() if 'Arduino Uno' in port.description]
    other_ports = [port.device for port in serial.tools.list_ports.comports() if 'Arduino Uno' not in port.description]
    all_ports = arduino_ports + other_ports

    # Iterate through detected ports and attempt handshake
    for port in all_ports:
        try:
            plugin._logger.info(f"Trying to connect to {port}...")
            plugin._plugin_manager.send_plugin_message(plugin._identifier, dict(type="log", message=f"Trying to connect to {port}..."))
            ser = serial.Serial(port, 9600, timeout=2)
            time.sleep(2)

            # Send handshake message 'Octoprint' with calculated parity bit
            plugin._logger.info("Sending handshake message 'Octoprint'...")
            plugin._plugin_manager.send_plugin_message(plugin._identifier, dict(type="log", message="Sending handshake message 'Octoprint'..."))
            message = 'Octoprint'
            parity_bit = parity_of(int(message, 36))
            plugin._logger.info(f"Parity bit for 'Octoprint': {parity_bit}")
            plugin._plugin_manager.send_plugin_message(plugin._identifier, dict(type="log", message=f"Parity bit for 'Octoprint': {parity_bit}"))
            ser.write((message + str(parity_bit) + '\n').encode())
            time.sleep(1)

            # Read response from Swapper3D device
            response = ser.readline().decode('utf-8').strip()
            plugin._logger.info(f"Received: {response}")
            plugin._plugin_manager.send_plugin_message(plugin._identifier, dict(type="log", message=f"Received: {response}"))

            # Check if handshake is successful
            if response == 'Swapper3D':
                plugin._logger.info("Handshake successful!")
                plugin._plugin_manager.send_plugin_message(plugin._identifier, dict(type="log", message="Handshake successful!"))
                # Update plugin settings with detected port and baud rate
                plugin._settings.set(["serialPort"], port)
                plugin._settings.set(["baudrate"], ser.baudrate)
                return ser, None  # Return None as the second value

            # Close connection if handshake failed
            plugin._logger.info("Handshake failed, closing connection.")
            plugin._plugin_manager.send_plugin_message(plugin._identifier, dict(type="log",
            message="Handshake failed, closing connection."))
            ser.close()

            return None, f"Failed to handshake with the device on port {port}"
        except serial.SerialException as e:
            plugin._logger.error(f"Failed to connect to {port}: {e}")
            plugin._plugin_manager.send_plugin_message(plugin._identifier, dict(type="log", message=f"Failed to connect to {port}: {e}"))
    return None, "Failed to connect to any port"

