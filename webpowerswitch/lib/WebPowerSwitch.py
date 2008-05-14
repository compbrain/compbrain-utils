#!/usr/bin/python
# $Id$
# $URL$

"""Control a webpowerswitch.com II PDU

Simple python class for controlling a Web Power Switch from
Digital Loggers, Inc - http://www.digital-loggers.com/lpc.html
"""

__author__ = 'compbrain@gmail.com (Will Nowak)'

import urllib
import re
import time

NUMOUTLETS = 8
STATUS_MATCH = re.compile(r'\<a href=outlet\?([1-8])=(ON|OFF)\>')
BOOLEAN_ONOFF_TABLE = {True:'ON', False:'OFF'}

class WebPowerSwitchException(Exception):
  def __init__(self, value):
    self.value = value

  def __str__(self):
    return repr(self.value)

class WebPowerSwitch:
  def __init__(self, user, password, ip=None, port=None):
    ''' Initialize the PDU controller class '''
    self._setUser(user)
    self._setPassword(password)
    self._setPort(port)
    self._setIP(ip)

  ##### Begin Get/Set Methods #####
  def _setUser(self, user):
    ''' Set a username to use for authentication to the PDU '''
    self._username = user

  def user(self):
    ''' Get the username to use for authentication to the PDU '''
    return self._username

  def _setPassword(self, password):
    ''' Set a username to use for authentication to the PDU '''
    self._password = password

  def password(self):
    ''' Get the password to use for authentication to the PDU '''
    return self._password

  def _setPort(self, port=None):
    ''' Set a port to use for communication to the PDU '''
    if port is None:
      port = 80
    self._port = port

  def port(self):
    ''' Get the port to use for communication to the PDU '''
    return self._port

  def _setIP(self, ip=None):
    ''' Set an IP to use for communication to the PDU '''
    if ip is None:
      ip = '192.168.0.100'
    self._ip = ip

  def ip(self):
    ''' Get the IP to use for communication to the PDU '''
    return self._ip

  def baseURL(self):
    ''' Get the Base URL to use for communication to the PDU
        This composes the username, password, IP and password together
    '''
    return 'http://%s:%s@%s:%s' % (self.user(), self.password(), self.ip(),
                                   self.port())
  ##### End Get/Set Methods #####

  def validOutlet(self, outlet_number):
    ''' Check if an outlet number is valid '''
    return outlet_number in range(1, NUMOUTLETS + 1)

  def validOperation(self, operation_symbol):
    ''' Determine if an operation symbol is valid '''
    return operation_symbol in ['ON', 'OFF', 'CCL']

  def _operation(self, outlet_number, operation_symbol):
    ''' General operation call wrapper for per-port commands '''
    if not self.validOperation(operation_symbol):
      raise WebPowerSwitchException('Invalid operation_symbol %s' %
                                    operation_symbol)
    if not self.validOutlet(outlet_number):
      raise WebPowerSwitchException('Invalid outlet_number %s' %
                                    outlet_number)
    self._operationCall(outlet_number, operation_symbol)

  def _alloperation(self, operation_symbol):
    ''' General operation call wrapper for all-port commands '''
    if not self.validOperation(operation_symbol):
      raise WebPowerSwitchException('Invalid operation_symbol %s' %
                                    operation_symbol)
    self._operationCall('a', operation_symbol)

  def _operationCall(self, outletcode, operation_symbol):
    ''' Low level operation call wrapper, actually communicates the operation
        to the PDU for execution
    '''
    url = '%s/outlet?%s=%s' % (self.baseURL(), outletcode, operation_symbol)
    request = urllib.urlopen(url)
    result = request.read()
    request.close()
    return result

  def on(self, outlet_number):
    ''' Turn on an outlet '''
    self._operation(outlet_number, 'ON')

  def all_on(self):
    ''' Turn on all outlets '''
    self._alloperation('ON')

  def off(self, outlet_number):
    ''' Turn off an outlet '''
    self._operation(outlet_number, 'OFF')

  def all_off(self):
    ''' Turn off all outlets '''
    self._alloperation('OFF')

  def cycle(self, outlet_number, method='software'):
    ''' Power cycle an outlet
        Uses software by default:
         - Send a power off command
         - Wait 1 second
         - Send a power on command
        Can also use the PDU's built in cycle command by setting method to
        'hardware'
    '''
    if method == 'software':
      self._operation(outlet_number, 'OFF')
      time.sleep(1)
      self._operation(outlet_number, 'ON')
    else:
      self._operation(outlet_number, 'CCL')

  def all_cycle(self, method='software'):
    ''' Same as cycle, but executes for all outlets '''
    if method == 'software':
      self._alloperation('OFF')
      time.sleep(1)
      self._alloperation('ON')
    else:
      self._alloperation('CCL')
