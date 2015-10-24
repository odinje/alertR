#!/usr/bin/python2

# written by sqall
# twitter: https://twitter.com/sqall01
# blog: http://blog.h4des.org
# github: https://github.com/sqall01
#
# Licensed under the GNU Public License, version 2.

import time
import random
import os
import logging
import smtplib
import threading


# internal class that holds the important attributes
# for a alert to work with (this class must be inherited from the
# used alert class)
class _Alert:

	def __init__(self):
		self.id = None
		self.description = None
		self.alertLevels = list()


	def triggerAlert(self, asyncAlertExecInstance):
		raise NotImplementedError("Function not implemented yet.")


	def stopAlert(self, asyncAlertExecInstance):
		raise NotImplementedError("Function not implemented yet.")


	def initializeAlert(self):
		raise NotImplementedError("Function not implemented yet.")


# this class represents an alert that sends a notification via mail
# to the configured address 
class MailAlert(_Alert):

	def __init__(self):
		_Alert.__init__(self)

		self.fileName = os.path.basename(__file__)

		# this flag is used to signalize if the alert is triggered or not
		self.triggered = None

		# these are the mail settings
		self.host = None
		self.port = None
		self.fromAddr = None
		self.toAddr = None
		self.subject = None
		self.templateFile = None

		self.bodyText = None


	# this function is called once when the alert client has connected itself
	# to the server (should be use to initialize everything that is needed
	# for the alert)
	def initializeAlert(self):

		# set the state of the alert to "not triggered"
		self.triggered = False

		with open(self.templateFile, 'r') as fp:
			self.bodyText = fp.read()


	def triggerAlert(self, asyncAlertExecInstance):

		# create a received message text
		if (asyncAlertExecInstance.dataTransfer
			and "message" in asyncAlertExecInstance.data):
			receivedMessage = asyncAlertExecInstance.data["message"]
		else:
			receivedMessage = "None"

		sensorDescription = asyncAlertExecInstance.sensorDescription

		# convert state to a text
		if asyncAlertExecInstance.state == 0:
			stateMessage = "Normal"
		elif asyncAlertExecInstance.state == 1:
			stateMessage = "Triggered"
		else:
			stateMessage = "Undefined"

		# replace wildcards with the actual values
		tempMsg = self.bodyText.replace("$MESSAGE$", receivedMessage)
		tempMsg = tempMsg.replace("$STATE$", stateMessage)
		tempMsg = tempMsg.replace("$SENSORDESC$", sensorDescription)

		emailHeader = "From: %s\r\nTo: %s\r\nSubject: %s\r\n" \
			% (self.fromAddr, self.toAddr, self.subject)

		try:
			logging.info("[%s] Sending eMail for triggered alert."
				% self.fileName)
			smtpServer = smtplib.SMTP(self.host, self.port)
			smtpServer.sendmail(self.fromAddr, self.toAddr, 
				emailHeader + tempMsg)
			smtpServer.quit()

		except Exception as e:
			logging.exception("[%s]: Unable to send eMail for "
				% self.fileName
				+ "triggered alert.")


	def stopAlert(self, asyncAlertExecInstance):
		pass


# this class is used to trigger or stop an alert
# in an own thread to not block the initiating thread
class AsynchronousAlertExecuter(threading.Thread):

	def __init__(self, alert):
		threading.Thread.__init__(self)

		self.fileName = os.path.basename(__file__)
		self.alert = alert

		# this option is used when the thread should
		# trigger an alert
		self.triggerAlert = False

		# this option is used when the thread should
		# stop an alert
		self.stopAlert = False

		# this options are used to transfer data from the received
		# sensor alert to the alert that is triggered
		self.sensorDescription = None
		self.dataTransfer = False # true or false
		self.data = None # only evaluated if data transfer is true
		self.state = None # (triggered = 1; back to normal = 0)


	def run(self):

		# check if an alert should be triggered
		if self.triggerAlert:
			self.alert.triggerAlert(self)

		# check if an alert should be stopped
		elif self.stopAlert:
			self.alert.stopAlert(self)