from odoo import models, fields, api
from odoo.exceptions import UserError
import platform
import subprocess

import logging

_logger = logging.getLogger(__name__)

class PosConfig(models.Model):
    _inherit = 'pos.config'

    def open_session_cb(self, check_coa=True):
        _logger.info("open_session_cb")
        def get_serial_number():
            system = platform.system()
            _logger.info("system:", str(system))
            if system == 'Windows':
                _logger.info("Windows System")
                try:
                    _logger.info("Windows Try")
                    # Run the PowerShell command to retrieve the Windows serial number
                    command = "powershell -Command \"wmic bios get serialnumber\""
                    output = subprocess.check_output(command, shell=True).decode().strip()
                    output = output.replace("SerialNumber","").replace("\r", "").replace("\n", "").replace(" ","")
                    return output
                except Exception as e:
                    _logger.info("Windows Except")
                    _logger.info("Error:", str(e))
                    return None
            elif system == 'Linux':
                _logger.info("Linux System")
                try:
                    _logger.info("Linux Try")
                    # Use the dmidecode command to retrieve the serial number from the BIOS
                    output = subprocess.check_output("sudo dmidecode -t system | grep 'Serial Number'",
                                                     shell=True).decode()

                    _logger.info(output)
                    _logger.info("output:", str(output))
                    # Extract the serial number from the output
                    serial_number = output.split(":")[1].strip()
                    return serial_number
                except Exception as e:
                    _logger.info("Linux Except")
                    _logger.info("Error:", str(e))
                    return None
            else:
                _logger.info("Unsupported operating system:", system)
                return None

        user = self.env.user
        if user.machine_type == 'laptop':

            # Call the function to retrieve the serial number
            serial_number = get_serial_number()
            _logger.info("Serial number: %s", serial_number)
            if serial_number:
                if serial_number != user.serial_number:
                    _logger.info("Serial number: %s", serial_number)
                    raise UserError('Access Denied. Sorry, you are not allowed to proceed. Registered serial number %s is not equal to your machine serial number %s.' % (user.serial_number, serial_number))
            else:
                raise UserError('Unable to get system serial number.')

        elif user.machine_type == 'tablet':
            # Call the function to retrieve the IMEI number
            _logger.info("Tablet login")

        # Invoke the parent class's method
        res = super(PosConfig, self).open_session_cb(check_coa)
        return res

