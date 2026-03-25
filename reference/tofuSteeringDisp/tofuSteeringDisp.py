# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

######################################################################################
# tofuSteeringDisp.py
# Tofu Express
# https://www.youtube.com/channel/UCgLYCKjBtZmO41tdpL1VPZw
# 2021-08-29	v0.51	first version based on dkSteeringWheel v0.5
#
# Original: dkSteeringWheel.py
# Dennis Karlsson (dennis@dennis.se)
# This is my take on the Steering Wheel app.
# Original: https://www.racedepartment.com/downloads/steering-input-display.11713/
# Version I started from: https://www.racedepartment.com/downloads/steering-input-display-esotic-mod.13570/
#
# 2018-09-02	v0.1	First version
# 2018-09-10	v0.2	Added option for inverted steering wheel colors. Bugfixes
# 2019-01-05	v0.3	Made the top marker a little nicer.
#						Updated dkConfigHandler.
# 2020-01-03	v0.4	Added ingame configuration.
#						Added option "Only draw if off center".
# 2020-01-06	v0.5	Added outline to spokes.
#						Fixed bug.
#
######################################################################################

import ac, acsys, math, time, dkCH
app = "tofuSteeringDisp"
ac.log("["+app+"] Starting...")

def strToBool(s):
	if s == 'True':
		return True
	elif s == 'False':
		return False
	else:
		ac.log("["+app+"] StrToBool error.")

# Handle config
dkCH.init(app)
dkSteeringWheelSettingsBackgroundOpacity		= float(dkCH.rc(app, app, 'backgroundopacity', '0.0'))
dkSteeringWheelSettingsDrawBorder				= int(dkCH.rc(app, app, 'drawborder', '0'))
dkSteeringWheelSettingsOnlyOffCenter			= strToBool(dkCH.rc(app, app, 'onlyoffcenter', 'False'))		# ingame conf
dkSteeringWheelSettingsMaxSpeed					= int(dkCH.rc(app, app, 'maxspeed', '1000'))					# ingame conf
dkSteeringWheelSettingsBlink					= strToBool(dkCH.rc(app, app, 'blink', 'False'))					# ingame conf
dkSteeringWheelSettingsPaintRed					= strToBool(dkCH.rc(app, app, 'paintred', 'False'))				# ingame conf
dkSteeringWheelSettingsLimitWheelAngle			= strToBool(dkCH.rc(app, app, 'limitwheelangle', 'False'))		# ingame conf
dkSteeringWheelSettingsOutline					= strToBool(dkCH.rc(app, app, 'outline', 'False'))				# ingame conf
dkSteeringWheelSettingsAppWidth					= int(dkCH.rc(app, app, 'appsize', '120'))						# ingame conf
dkSteeringWheelSettingsMaxDegrees				= int(dkCH.rc(app, app, 'maxdegrees', '900'))					# ingame conf
dkSteeringWheelSettingsMarker					= strToBool(dkCH.rc(app, app, 'marker', 'True'))				# ingame conf
dkSteeringWheelSettingsMarkerTopSpeed			= int(dkCH.rc(app, app, 'markertopspeed', '1000'))				# ingame conf
dkSteeringWheelSettingsSpokes					= strToBool(dkCH.rc(app, app, 'spokes', 'True'))				# ingame conf
dkSteeringWheelSettingsSpokesWidth				= int(dkCH.rc(app, app, 'spokeswidth', '50'))					# ingame conf
dkSteeringWheelSettingsInvertWheelColor			= strToBool(dkCH.rc(app, app, 'invertwheelcolor', 'False'))		# ingame conf

ac.log("["+app+"] Configuration applied...")

appHeight				= dkSteeringWheelSettingsAppWidth+25
appWindow				= 0

dkSteeringWheelConfigButtonTimer = 0
configWindowXOffset		= -250
configWindowYOffset		= -50
configWindowVisible 	= False

def acMain(ac_version):
	global appWindow, app
	
	neededSpace = 0

	appWindow = ac.newApp(app)
	ac.setSize(appWindow, dkSteeringWheelSettingsAppWidth, appHeight)
	ac.setTitle(appWindow, "")
	ac.setIconPosition(appWindow, 0, -10000)
	ac.drawBorder(appWindow, dkSteeringWheelSettingsDrawBorder)

	### Config window
	ac.addOnClickedListener(appWindow, appClick)

	# Configure button
	global dkSteeringWheelConfigButton
	dkSteeringWheelConfigButton = ac.addButton(appWindow, "Configure "+app);
	ac.setBackgroundColor(dkSteeringWheelConfigButton, 0, 0, 0)
	ac.drawBackground(dkSteeringWheelConfigButton, 1)
	ac.setVisible(dkSteeringWheelConfigButton, 0)
	ac.setFontAlignment(dkSteeringWheelConfigButton, "center")
	ac.drawBorder(dkSteeringWheelConfigButton, 1)
	ac.setFontColor(dkSteeringWheelConfigButton, 1, 1, 1, 1)
	ac.setFontSize(dkSteeringWheelConfigButton, 14)
	ac.setSize(dkSteeringWheelConfigButton, 180, 20)
	ac.setPosition(dkSteeringWheelConfigButton, 2, 5)
	ac.addOnClickedListener(dkSteeringWheelConfigButton, dkSteeringWheelConfigButtonClick)

	# Configuration background
	global dkSteeringWheelConfigBackground
	dkSteeringWheelConfigBackground = ac.addButton(appWindow, "")
	ac.setBackgroundColor(dkSteeringWheelConfigBackground, 0, 0, 0)
	ac.setVisible(dkSteeringWheelConfigBackground, 0)	
	ac.setBackgroundOpacity(dkSteeringWheelConfigBackground, 0.8)
	ac.drawBorder(dkSteeringWheelConfigBackground, 0)
	ac.drawBackground(dkSteeringWheelConfigBackground, 1)
	ac.setSize(dkSteeringWheelConfigBackground, 240, 320)
	ac.setPosition(dkSteeringWheelConfigBackground, configWindowXOffset-3, configWindowYOffset+0)

	# Configuration background label
	global dkSteeringWheelSettingsConfigLabel
	dkSteeringWheelSettingsConfigLabel = ac.addLabel(appWindow, app)
	ac.setFontColor(dkSteeringWheelSettingsConfigLabel, 1, 1, 1, 1)
	ac.setFontAlignment(dkSteeringWheelSettingsConfigLabel, "left")
	ac.setFontSize(dkSteeringWheelSettingsConfigLabel, 18)
	ac.setPosition(dkSteeringWheelSettingsConfigLabel, configWindowXOffset+50, configWindowYOffset+0)
	ac.setVisible(dkSteeringWheelSettingsConfigLabel, 0)

	##########################################################################################################
	# Only draw if off center
	global dkSteeringWheelSettingsOnlyOffCenterCheckbox
	neededSpace += 40
	dkSteeringWheelSettingsOnlyOffCenterCheckbox = ac.addCheckBox(appWindow, "Only draw if off center")
	ac.setValue(dkSteeringWheelSettingsOnlyOffCenterCheckbox, dkSteeringWheelSettingsOnlyOffCenter)
	ac.setVisible(dkSteeringWheelSettingsOnlyOffCenterCheckbox, 0)
	ac.setSize(dkSteeringWheelSettingsOnlyOffCenterCheckbox, 12, 12)
	ac.setPosition(dkSteeringWheelSettingsOnlyOffCenterCheckbox, configWindowXOffset+11, configWindowYOffset+neededSpace)
	ac.addOnCheckBoxChanged(dkSteeringWheelSettingsOnlyOffCenterCheckbox, dkSteeringWheelSettingsDoOnlyOffCenterCheckbox)
	##########################################################################################################

	##########################################################################################################
	# Blink
	global dkSteeringWheelSettingsBlinkCheckbox
	neededSpace += 20
	dkSteeringWheelSettingsBlinkCheckbox = ac.addCheckBox(appWindow, "Blink if not centered")
	ac.setValue(dkSteeringWheelSettingsBlinkCheckbox, dkSteeringWheelSettingsBlink)
	ac.setVisible(dkSteeringWheelSettingsBlinkCheckbox, 0)
	ac.setSize(dkSteeringWheelSettingsBlinkCheckbox, 12, 12)
	ac.setPosition(dkSteeringWheelSettingsBlinkCheckbox, configWindowXOffset+11, configWindowYOffset+neededSpace)
	ac.addOnCheckBoxChanged(dkSteeringWheelSettingsBlinkCheckbox, dkSteeringWheelSettingsDoBlinkCheckbox)
	##########################################################################################################

	##########################################################################################################
	# Paint red
	global dkSteeringWheelSettingsPaintRedCheckbox
	neededSpace += 20
	dkSteeringWheelSettingsPaintRedCheckbox = ac.addCheckBox(appWindow, "Paint red if not centered")
	ac.setValue(dkSteeringWheelSettingsPaintRedCheckbox, dkSteeringWheelSettingsPaintRed)
	ac.setVisible(dkSteeringWheelSettingsPaintRedCheckbox, 0)
	ac.setSize(dkSteeringWheelSettingsPaintRedCheckbox, 12, 12)
	ac.setPosition(dkSteeringWheelSettingsPaintRedCheckbox, configWindowXOffset+11, configWindowYOffset+neededSpace)
	ac.addOnCheckBoxChanged(dkSteeringWheelSettingsPaintRedCheckbox, dkSteeringWheelSettingsDoPaintRedCheckbox)
	##########################################################################################################

	##########################################################################################################
	# Limit wheel angle
	global dkSteeringWheelSettingsLimitWheelAngleCheckbox
	neededSpace += 20
	dkSteeringWheelSettingsLimitWheelAngleCheckbox = ac.addCheckBox(appWindow, "Limit wheel angle")
	ac.setValue(dkSteeringWheelSettingsLimitWheelAngleCheckbox, dkSteeringWheelSettingsLimitWheelAngle)
	ac.setVisible(dkSteeringWheelSettingsLimitWheelAngleCheckbox, 0)
	ac.setSize(dkSteeringWheelSettingsLimitWheelAngleCheckbox, 12, 12)
	ac.setPosition(dkSteeringWheelSettingsLimitWheelAngleCheckbox, configWindowXOffset+11, configWindowYOffset+neededSpace)
	ac.addOnCheckBoxChanged(dkSteeringWheelSettingsLimitWheelAngleCheckbox, dkSteeringWheelSettingsDoLimitWheelAngleCheckbox)
	##########################################################################################################

	##########################################################################################################
	# Outline
	global dkSteeringWheelSettingsLimitWheelOutlineCheckbox 
	neededSpace += 20
	dkSteeringWheelSettingsLimitWheelOutlineCheckbox = ac.addCheckBox(appWindow, "Draw wheel outline")
	ac.setValue(dkSteeringWheelSettingsLimitWheelOutlineCheckbox, dkSteeringWheelSettingsOutline)
	ac.setVisible(dkSteeringWheelSettingsLimitWheelOutlineCheckbox, 0)
	ac.setSize(dkSteeringWheelSettingsLimitWheelOutlineCheckbox, 12, 12)
	ac.setPosition(dkSteeringWheelSettingsLimitWheelOutlineCheckbox, configWindowXOffset+11, configWindowYOffset+neededSpace)
	ac.addOnCheckBoxChanged(dkSteeringWheelSettingsLimitWheelOutlineCheckbox, dkSteeringWheelSettingsDoLimitWheelOutlineCheckbox)
	##########################################################################################################

	##########################################################################################################
	# Marker
	global dkSteeringWheelSettingsWheelMarkerCheckbox
	neededSpace += 20
	dkSteeringWheelSettingsWheelMarkerCheckbox = ac.addCheckBox(appWindow, "Draw wheel marker")
	ac.setValue(dkSteeringWheelSettingsWheelMarkerCheckbox, dkSteeringWheelSettingsMarker)
	ac.setVisible(dkSteeringWheelSettingsWheelMarkerCheckbox, 0)
	ac.setSize(dkSteeringWheelSettingsWheelMarkerCheckbox, 12, 12)
	ac.setPosition(dkSteeringWheelSettingsWheelMarkerCheckbox, configWindowXOffset+11, configWindowYOffset+neededSpace)
	ac.addOnCheckBoxChanged(dkSteeringWheelSettingsWheelMarkerCheckbox, dkSteeringWheelSettingsDoWheelMarkerCheckbox)
	##########################################################################################################

	##########################################################################################################
	# Spokes
	global dkSteeringWheelSettingsWheelSpokesCheckbox
	neededSpace += 20
	dkSteeringWheelSettingsWheelSpokesCheckbox = ac.addCheckBox(appWindow, "Draw spokes & hub")
	ac.setValue(dkSteeringWheelSettingsWheelSpokesCheckbox, dkSteeringWheelSettingsSpokes)
	ac.setVisible(dkSteeringWheelSettingsWheelSpokesCheckbox, 0)
	ac.setSize(dkSteeringWheelSettingsWheelSpokesCheckbox, 12, 12)
	ac.setPosition(dkSteeringWheelSettingsWheelSpokesCheckbox, configWindowXOffset+11, configWindowYOffset+neededSpace)
	ac.addOnCheckBoxChanged(dkSteeringWheelSettingsWheelSpokesCheckbox, dkSteeringWheelSettingsDoWheelSpokesCheckbox)
	##########################################################################################################

	##########################################################################################################
	# Invert
	global dkSteeringWheelSettingsWheelInvertColorCheckbox
	neededSpace += 20
	dkSteeringWheelSettingsWheelInvertColorCheckbox = ac.addCheckBox(appWindow, "Invert wheel colors")
	ac.setValue(dkSteeringWheelSettingsWheelInvertColorCheckbox, dkSteeringWheelSettingsInvertWheelColor)
	ac.setVisible(dkSteeringWheelSettingsWheelInvertColorCheckbox, 0)
	ac.setSize(dkSteeringWheelSettingsWheelInvertColorCheckbox, 12, 12)
	ac.setPosition(dkSteeringWheelSettingsWheelInvertColorCheckbox, configWindowXOffset+11, configWindowYOffset+neededSpace)
	ac.addOnCheckBoxChanged(dkSteeringWheelSettingsWheelInvertColorCheckbox, dkSteeringWheelSettingsDoWheelInvertColorCheckbox)
	##########################################################################################################

	##########################################################################################################
	# App size
	global dkSteeringWheelSettingsWheelSettingsWheelSizeLabel, dkSteeringWheelSettingsWheelSettingsWheelSizeLabelActual, dkSteeringWheelSettingsWheelSettingsWheelSizeIncrease, dkSteeringWheelSettingsWheelSettingsWheelSizeDecrease
	neededSpace += 16
	dkSteeringWheelSettingsWheelSettingsWheelSizeLabel = ac.addLabel(appWindow, "Wheel size")
	ac.setBackgroundOpacity(dkSteeringWheelSettingsWheelSettingsWheelSizeLabel, 0)
	ac.setVisible(dkSteeringWheelSettingsWheelSettingsWheelSizeLabel, 0)
	ac.setFontAlignment(dkSteeringWheelSettingsWheelSettingsWheelSizeLabel, "left")
	ac.drawBorder(dkSteeringWheelSettingsWheelSettingsWheelSizeLabel, 0)
	ac.setFontColor(dkSteeringWheelSettingsWheelSettingsWheelSizeLabel, 1, 1, 1, 1)
	ac.setFontSize(dkSteeringWheelSettingsWheelSettingsWheelSizeLabel, 16)
	ac.setSize(dkSteeringWheelSettingsWheelSettingsWheelSizeLabel, 90, 20)
	ac.setPosition(dkSteeringWheelSettingsWheelSettingsWheelSizeLabel, configWindowXOffset+37, configWindowYOffset+neededSpace)

	dkSteeringWheelSettingsWheelSettingsWheelSizeLabelActual = ac.addLabel(appWindow, "("+str(dkSteeringWheelSettingsAppWidth)+")")
	ac.setBackgroundOpacity(dkSteeringWheelSettingsWheelSettingsWheelSizeLabelActual, 0)
	ac.setVisible(dkSteeringWheelSettingsWheelSettingsWheelSizeLabelActual, 0)
	ac.setFontAlignment(dkSteeringWheelSettingsWheelSettingsWheelSizeLabelActual, "left")
	ac.drawBorder(dkSteeringWheelSettingsWheelSettingsWheelSizeLabelActual, 0)
	ac.setFontColor(dkSteeringWheelSettingsWheelSettingsWheelSizeLabelActual, 1, 1, 1, 1)
	ac.setFontSize(dkSteeringWheelSettingsWheelSettingsWheelSizeLabelActual, 12)
	ac.setSize(dkSteeringWheelSettingsWheelSettingsWheelSizeLabelActual, 30, 20)
	ac.setPosition(dkSteeringWheelSettingsWheelSettingsWheelSizeLabelActual, configWindowXOffset+195, configWindowYOffset+neededSpace+3)

	dkSteeringWheelSettingsWheelSettingsWheelSizeIncrease = ac.addButton(appWindow, "+")
	ac.setVisible(dkSteeringWheelSettingsWheelSettingsWheelSizeIncrease, 0)
	ac.setFontAlignment(dkSteeringWheelSettingsWheelSettingsWheelSizeIncrease, "center")
	ac.drawBorder(dkSteeringWheelSettingsWheelSettingsWheelSizeIncrease, 1)
	ac.setFontColor(dkSteeringWheelSettingsWheelSettingsWheelSizeIncrease, 1, 1, 1, 1)
	ac.setFontSize(dkSteeringWheelSettingsWheelSettingsWheelSizeIncrease, 14)
	ac.setSize(dkSteeringWheelSettingsWheelSettingsWheelSizeIncrease, 15, 20)
	ac.setPosition(dkSteeringWheelSettingsWheelSettingsWheelSizeIncrease, configWindowXOffset+18, configWindowYOffset+neededSpace+1)
	ac.addOnClickedListener(dkSteeringWheelSettingsWheelSettingsWheelSizeIncrease, dkSteeringWheelSettingsDoWheelSettingsWheelSizeIncrease)

	dkSteeringWheelSettingsWheelSettingsWheelSizeDecrease = ac.addButton(appWindow, "-")
	ac.setVisible(dkSteeringWheelSettingsWheelSettingsWheelSizeDecrease, 0)
	ac.setFontAlignment(dkSteeringWheelSettingsWheelSettingsWheelSizeDecrease, "center")
	ac.drawBorder(dkSteeringWheelSettingsWheelSettingsWheelSizeDecrease, 1)
	ac.setFontColor(dkSteeringWheelSettingsWheelSettingsWheelSizeDecrease, 1, 1, 1, 1)
	ac.setFontSize(dkSteeringWheelSettingsWheelSettingsWheelSizeDecrease, 14)
	ac.setSize(dkSteeringWheelSettingsWheelSettingsWheelSizeDecrease, 15, 20)
	ac.setPosition(dkSteeringWheelSettingsWheelSettingsWheelSizeDecrease, configWindowXOffset, configWindowYOffset+neededSpace+1)
	ac.addOnClickedListener(dkSteeringWheelSettingsWheelSettingsWheelSizeDecrease, dkSteeringWheelSettingsDoWheelSettingsWheelSizeDecrease)
	##########################################################################################################

	##########################################################################################################
	# Max speed
	global dkSteeringWheelSettingsWheelSettingsMaxSpeedLabel, dkSteeringWheelSettingsWheelSettingsMaxSpeedLabelActual, dkSteeringWheelSettingsWheelSettingsMaxSpeedIncrease, dkSteeringWheelSettingsWheelSettingsMaxSpeedDecrease
	neededSpace += 22
	dkSteeringWheelSettingsWheelSettingsMaxSpeedLabel = ac.addLabel(appWindow, "Wheel max speed")
	ac.setBackgroundOpacity(dkSteeringWheelSettingsWheelSettingsMaxSpeedLabel, 0)
	ac.setVisible(dkSteeringWheelSettingsWheelSettingsMaxSpeedLabel, 0)
	ac.setFontAlignment(dkSteeringWheelSettingsWheelSettingsMaxSpeedLabel, "left")
	ac.drawBorder(dkSteeringWheelSettingsWheelSettingsMaxSpeedLabel, 0)
	ac.setFontColor(dkSteeringWheelSettingsWheelSettingsMaxSpeedLabel, 1, 1, 1, 1)
	ac.setFontSize(dkSteeringWheelSettingsWheelSettingsMaxSpeedLabel, 16)
	ac.setSize(dkSteeringWheelSettingsWheelSettingsMaxSpeedLabel, 90, 20)
	ac.setPosition(dkSteeringWheelSettingsWheelSettingsMaxSpeedLabel, configWindowXOffset+37, configWindowYOffset+neededSpace)

	dkSteeringWheelSettingsWheelSettingsMaxSpeedLabelActual = ac.addLabel(appWindow, "("+str(dkSteeringWheelSettingsMaxSpeed)+")")
	ac.setBackgroundOpacity(dkSteeringWheelSettingsWheelSettingsMaxSpeedLabelActual, 0)
	ac.setVisible(dkSteeringWheelSettingsWheelSettingsMaxSpeedLabelActual, 0)
	ac.setFontAlignment(dkSteeringWheelSettingsWheelSettingsMaxSpeedLabelActual, "left")
	ac.drawBorder(dkSteeringWheelSettingsWheelSettingsMaxSpeedLabelActual, 0)
	ac.setFontColor(dkSteeringWheelSettingsWheelSettingsMaxSpeedLabelActual, 1, 1, 1, 1)
	ac.setFontSize(dkSteeringWheelSettingsWheelSettingsMaxSpeedLabelActual, 12)
	ac.setSize(dkSteeringWheelSettingsWheelSettingsMaxSpeedLabelActual, 30, 20)
	ac.setPosition(dkSteeringWheelSettingsWheelSettingsMaxSpeedLabelActual, configWindowXOffset+195, configWindowYOffset+neededSpace+3)

	dkSteeringWheelSettingsWheelSettingsMaxSpeedIncrease = ac.addButton(appWindow, "+")
	ac.setVisible(dkSteeringWheelSettingsWheelSettingsMaxSpeedIncrease, 0)
	ac.setFontAlignment(dkSteeringWheelSettingsWheelSettingsMaxSpeedIncrease, "center")
	ac.drawBorder(dkSteeringWheelSettingsWheelSettingsMaxSpeedIncrease, 1)
	ac.setFontColor(dkSteeringWheelSettingsWheelSettingsMaxSpeedIncrease, 1, 1, 1, 1)
	ac.setFontSize(dkSteeringWheelSettingsWheelSettingsMaxSpeedIncrease, 14)
	ac.setSize(dkSteeringWheelSettingsWheelSettingsMaxSpeedIncrease, 15, 20)
	ac.setPosition(dkSteeringWheelSettingsWheelSettingsMaxSpeedIncrease, configWindowXOffset+18, configWindowYOffset+neededSpace+1)
	ac.addOnClickedListener(dkSteeringWheelSettingsWheelSettingsMaxSpeedIncrease, dkSteeringWheelSettingsDoWheelSettingsMaxSpeedIncrease)

	dkSteeringWheelSettingsWheelSettingsMaxSpeedDecrease = ac.addButton(appWindow, "-")
	ac.setVisible(dkSteeringWheelSettingsWheelSettingsMaxSpeedDecrease, 0)
	ac.setFontAlignment(dkSteeringWheelSettingsWheelSettingsMaxSpeedDecrease, "center")
	ac.drawBorder(dkSteeringWheelSettingsWheelSettingsMaxSpeedDecrease, 1)
	ac.setFontColor(dkSteeringWheelSettingsWheelSettingsMaxSpeedDecrease, 1, 1, 1, 1)
	ac.setFontSize(dkSteeringWheelSettingsWheelSettingsMaxSpeedDecrease, 14)
	ac.setSize(dkSteeringWheelSettingsWheelSettingsMaxSpeedDecrease, 15, 20)
	ac.setPosition(dkSteeringWheelSettingsWheelSettingsMaxSpeedDecrease, configWindowXOffset, configWindowYOffset+neededSpace+1)
	ac.addOnClickedListener(dkSteeringWheelSettingsWheelSettingsMaxSpeedDecrease, dkSteeringWheelSettingsDoWheelSettingsMaxSpeedDecrease)
	##########################################################################################################

	##########################################################################################################
	# Max speed marker
	global dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerLabel, dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerLabelActual, dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerIncrease, dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerDecrease
	neededSpace += 22
	dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerLabel = ac.addLabel(appWindow, "Marker max speed")
	ac.setBackgroundOpacity(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerLabel, 0)
	ac.setVisible(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerLabel, 0)
	ac.setFontAlignment(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerLabel, "left")
	ac.drawBorder(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerLabel, 0)
	ac.setFontColor(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerLabel, 1, 1, 1, 1)
	ac.setFontSize(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerLabel, 16)
	ac.setSize(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerLabel, 90, 20)
	ac.setPosition(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerLabel, configWindowXOffset+37, configWindowYOffset+neededSpace)

	dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerLabelActual = ac.addLabel(appWindow, "("+str(dkSteeringWheelSettingsMarkerTopSpeed)+")")
	ac.setBackgroundOpacity(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerLabelActual, 0)
	ac.setVisible(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerLabelActual, 0)
	ac.setFontAlignment(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerLabelActual, "left")
	ac.drawBorder(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerLabelActual, 0)
	ac.setFontColor(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerLabelActual, 1, 1, 1, 1)
	ac.setFontSize(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerLabelActual, 12)
	ac.setSize(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerLabelActual, 30, 20)
	ac.setPosition(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerLabelActual, configWindowXOffset+195, configWindowYOffset+neededSpace+3)

	dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerIncrease = ac.addButton(appWindow, "+")
	ac.setVisible(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerIncrease, 0)
	ac.setFontAlignment(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerIncrease, "center")
	ac.drawBorder(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerIncrease, 1)
	ac.setFontColor(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerIncrease, 1, 1, 1, 1)
	ac.setFontSize(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerIncrease, 14)
	ac.setSize(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerIncrease, 15, 20)
	ac.setPosition(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerIncrease, configWindowXOffset+18, configWindowYOffset+neededSpace+1)
	ac.addOnClickedListener(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerIncrease, dkSteeringWheelSettingsDoWheelSettingsMaxSpeedMarkerIncrease)

	dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerDecrease = ac.addButton(appWindow, "-")
	ac.setVisible(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerDecrease, 0)
	ac.setFontAlignment(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerDecrease, "center")
	ac.drawBorder(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerDecrease, 1)
	ac.setFontColor(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerDecrease, 1, 1, 1, 1)
	ac.setFontSize(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerDecrease, 14)
	ac.setSize(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerDecrease, 15, 20)
	ac.setPosition(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerDecrease, configWindowXOffset, configWindowYOffset+neededSpace+1)
	ac.addOnClickedListener(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerDecrease, dkSteeringWheelSettingsDoWheelSettingsMaxSpeedMarkerDecrease)
	##########################################################################################################

	##########################################################################################################
	# Max degrees
	global dkSteeringWheelSettingsWheelSettingsMaxDegreesLabel, dkSteeringWheelSettingsWheelSettingsMaxDegreesLabelActual, dkSteeringWheelSettingsWheelSettingsMaxDegreesIncrease, dkSteeringWheelSettingsWheelSettingsMaxDegreesDecrease
	neededSpace += 22
	dkSteeringWheelSettingsWheelSettingsMaxDegreesLabel = ac.addLabel(appWindow, "Max steering degrees")
	ac.setBackgroundOpacity(dkSteeringWheelSettingsWheelSettingsMaxDegreesLabel, 0)
	ac.setVisible(dkSteeringWheelSettingsWheelSettingsMaxDegreesLabel, 0)
	ac.setFontAlignment(dkSteeringWheelSettingsWheelSettingsMaxDegreesLabel, "left")
	ac.drawBorder(dkSteeringWheelSettingsWheelSettingsMaxDegreesLabel, 0)
	ac.setFontColor(dkSteeringWheelSettingsWheelSettingsMaxDegreesLabel, 1, 1, 1, 1)
	ac.setFontSize(dkSteeringWheelSettingsWheelSettingsMaxDegreesLabel, 16)
	ac.setSize(dkSteeringWheelSettingsWheelSettingsMaxDegreesLabel, 90, 20)
	ac.setPosition(dkSteeringWheelSettingsWheelSettingsMaxDegreesLabel, configWindowXOffset+37, configWindowYOffset+neededSpace)

	dkSteeringWheelSettingsWheelSettingsMaxDegreesLabelActual = ac.addLabel(appWindow, "("+str(dkSteeringWheelSettingsMaxDegrees)+")")
	ac.setBackgroundOpacity(dkSteeringWheelSettingsWheelSettingsMaxDegreesLabelActual, 0)
	ac.setVisible(dkSteeringWheelSettingsWheelSettingsMaxDegreesLabelActual, 0)
	ac.setFontAlignment(dkSteeringWheelSettingsWheelSettingsMaxDegreesLabelActual, "left")
	ac.drawBorder(dkSteeringWheelSettingsWheelSettingsMaxDegreesLabelActual, 0)
	ac.setFontColor(dkSteeringWheelSettingsWheelSettingsMaxDegreesLabelActual, 1, 1, 1, 1)
	ac.setFontSize(dkSteeringWheelSettingsWheelSettingsMaxDegreesLabelActual, 12)
	ac.setSize(dkSteeringWheelSettingsWheelSettingsMaxDegreesLabelActual, 30, 20)
	ac.setPosition(dkSteeringWheelSettingsWheelSettingsMaxDegreesLabelActual, configWindowXOffset+195, configWindowYOffset+neededSpace+3)

	dkSteeringWheelSettingsWheelSettingsMaxDegreesIncrease = ac.addButton(appWindow, "+")
	ac.setVisible(dkSteeringWheelSettingsWheelSettingsMaxDegreesIncrease, 0)
	ac.setFontAlignment(dkSteeringWheelSettingsWheelSettingsMaxDegreesIncrease, "center")
	ac.drawBorder(dkSteeringWheelSettingsWheelSettingsMaxDegreesIncrease, 1)
	ac.setFontColor(dkSteeringWheelSettingsWheelSettingsMaxDegreesIncrease, 1, 1, 1, 1)
	ac.setFontSize(dkSteeringWheelSettingsWheelSettingsMaxDegreesIncrease, 14)
	ac.setSize(dkSteeringWheelSettingsWheelSettingsMaxDegreesIncrease, 15, 20)
	ac.setPosition(dkSteeringWheelSettingsWheelSettingsMaxDegreesIncrease, configWindowXOffset+18, configWindowYOffset+neededSpace+1)
	ac.addOnClickedListener(dkSteeringWheelSettingsWheelSettingsMaxDegreesIncrease, dkSteeringWheelSettingsDoWheelSettingsMaxDegreesIncrease)

	dkSteeringWheelSettingsWheelSettingsMaxDegreesDecrease = ac.addButton(appWindow, "-")
	ac.setVisible(dkSteeringWheelSettingsWheelSettingsMaxDegreesDecrease, 0)
	ac.setFontAlignment(dkSteeringWheelSettingsWheelSettingsMaxDegreesDecrease, "center")
	ac.drawBorder(dkSteeringWheelSettingsWheelSettingsMaxDegreesDecrease, 1)
	ac.setFontColor(dkSteeringWheelSettingsWheelSettingsMaxDegreesDecrease, 1, 1, 1, 1)
	ac.setFontSize(dkSteeringWheelSettingsWheelSettingsMaxDegreesDecrease, 14)
	ac.setSize(dkSteeringWheelSettingsWheelSettingsMaxDegreesDecrease, 15, 20)
	ac.setPosition(dkSteeringWheelSettingsWheelSettingsMaxDegreesDecrease, configWindowXOffset, configWindowYOffset+neededSpace+1)
	ac.addOnClickedListener(dkSteeringWheelSettingsWheelSettingsMaxDegreesDecrease, dkSteeringWheelSettingsDoWheelSettingsMaxDegreesDecrease)
	##########################################################################################################

	##########################################################################################################
	# Spokes width
	global dkSteeringWheelSettingsWheelSettingsSpokesWidthLabel, dkSteeringWheelSettingsWheelSettingsSpokesWidthLabelActual, dkSteeringWheelSettingsWheelSettingsSpokesWidthIncrease, dkSteeringWheelSettingsWheelSettingsSpokesWidthDecrease
	neededSpace += 22
	dkSteeringWheelSettingsWheelSettingsSpokesWidthLabel = ac.addLabel(appWindow, "Spokes width")
	ac.setBackgroundOpacity(dkSteeringWheelSettingsWheelSettingsSpokesWidthLabel, 0)
	ac.setVisible(dkSteeringWheelSettingsWheelSettingsSpokesWidthLabel, 0)
	ac.setFontAlignment(dkSteeringWheelSettingsWheelSettingsSpokesWidthLabel, "left")
	ac.drawBorder(dkSteeringWheelSettingsWheelSettingsSpokesWidthLabel, 0)
	ac.setFontColor(dkSteeringWheelSettingsWheelSettingsSpokesWidthLabel, 1, 1, 1, 1)
	ac.setFontSize(dkSteeringWheelSettingsWheelSettingsSpokesWidthLabel, 16)
	ac.setSize(dkSteeringWheelSettingsWheelSettingsSpokesWidthLabel, 90, 20)
	ac.setPosition(dkSteeringWheelSettingsWheelSettingsSpokesWidthLabel, configWindowXOffset+37, configWindowYOffset+neededSpace)

	dkSteeringWheelSettingsWheelSettingsSpokesWidthLabelActual = ac.addLabel(appWindow, "("+str(dkSteeringWheelSettingsSpokesWidth)+")")
	ac.setBackgroundOpacity(dkSteeringWheelSettingsWheelSettingsSpokesWidthLabelActual, 0)
	ac.setVisible(dkSteeringWheelSettingsWheelSettingsSpokesWidthLabelActual, 0)
	ac.setFontAlignment(dkSteeringWheelSettingsWheelSettingsSpokesWidthLabelActual, "left")
	ac.drawBorder(dkSteeringWheelSettingsWheelSettingsSpokesWidthLabelActual, 0)
	ac.setFontColor(dkSteeringWheelSettingsWheelSettingsSpokesWidthLabelActual, 1, 1, 1, 1)
	ac.setFontSize(dkSteeringWheelSettingsWheelSettingsSpokesWidthLabelActual, 12)
	ac.setSize(dkSteeringWheelSettingsWheelSettingsSpokesWidthLabelActual, 30, 20)
	ac.setPosition(dkSteeringWheelSettingsWheelSettingsSpokesWidthLabelActual, configWindowXOffset+195, configWindowYOffset+neededSpace+3)

	dkSteeringWheelSettingsWheelSettingsSpokesWidthIncrease = ac.addButton(appWindow, "+")
	ac.setVisible(dkSteeringWheelSettingsWheelSettingsSpokesWidthIncrease, 0)
	ac.setFontAlignment(dkSteeringWheelSettingsWheelSettingsSpokesWidthIncrease, "center")
	ac.drawBorder(dkSteeringWheelSettingsWheelSettingsSpokesWidthIncrease, 1)
	ac.setFontColor(dkSteeringWheelSettingsWheelSettingsSpokesWidthIncrease, 1, 1, 1, 1)
	ac.setFontSize(dkSteeringWheelSettingsWheelSettingsSpokesWidthIncrease, 14)
	ac.setSize(dkSteeringWheelSettingsWheelSettingsSpokesWidthIncrease, 15, 20)
	ac.setPosition(dkSteeringWheelSettingsWheelSettingsSpokesWidthIncrease, configWindowXOffset+18, configWindowYOffset+neededSpace+1)
	ac.addOnClickedListener(dkSteeringWheelSettingsWheelSettingsSpokesWidthIncrease, dkSteeringWheelSettingsDoWheelSettingsSpokesWidthIncrease)

	dkSteeringWheelSettingsWheelSettingsSpokesWidthDecrease = ac.addButton(appWindow, "-")
	ac.setVisible(dkSteeringWheelSettingsWheelSettingsSpokesWidthDecrease, 0)
	ac.setFontAlignment(dkSteeringWheelSettingsWheelSettingsSpokesWidthDecrease, "center")
	ac.drawBorder(dkSteeringWheelSettingsWheelSettingsSpokesWidthDecrease, 1)
	ac.setFontColor(dkSteeringWheelSettingsWheelSettingsSpokesWidthDecrease, 1, 1, 1, 1)
	ac.setFontSize(dkSteeringWheelSettingsWheelSettingsSpokesWidthDecrease, 14)
	ac.setSize(dkSteeringWheelSettingsWheelSettingsSpokesWidthDecrease, 15, 20)
	ac.setPosition(dkSteeringWheelSettingsWheelSettingsSpokesWidthDecrease, configWindowXOffset, configWindowYOffset+neededSpace+1)
	ac.addOnClickedListener(dkSteeringWheelSettingsWheelSettingsSpokesWidthDecrease, dkSteeringWheelSettingsDoWheelSettingsSpokesWidthDecrease)
	##########################################################################################################

	#showConfigWindow(True)

	ac.addRenderCallback(appWindow, onFormRender)
	return app

def acUpdate(deltaT):
	return

def acShutdown():
	global app
	ac.log("["+app+"] Closing...")

def appClick(name, state): # Show configuration button if user clicks on app window
	global app, dkSteeringWheelConfigButton, dkSteeringWheelConfigButtonTimer
	ac.setVisible(dkSteeringWheelConfigButton, 1)
	dkSteeringWheelConfigButtonTimer = time.clock()

def dkSteeringWheelConfigButtonClick(name, state): # Show configuration window if user clicks on Configure button
	global app, dkSteeringWheelConfigButton, dkSteeringWheelConfigButtonTimer, configWindowVisible
	ac.setVisible(dkSteeringWheelConfigButton, 0)
	dkSteeringWheelConfigButtonTimer = 0 ###
	if configWindowVisible:
		ac.setVisible(dkSteeringWheelConfigButton, 0)
		showConfigWindow(0)
		configWindowVisible = False
	else:
		ac.setVisible(dkSteeringWheelConfigButton, 1)
		showConfigWindow(1)
		configWindowVisible = True

def showConfigWindow(state):
	global app
	global dkSteeringWheelConfigBackground, dkSteeringWheelSettingsConfigLabel
	global dkSteeringWheelSettingsOnlyOffCenterCheckbox, dkSteeringWheelSettingsBlinkCheckbox, dkSteeringWheelSettingsPaintRedCheckbox, dkSteeringWheelSettingsLimitWheelAngleCheckbox, dkSteeringWheelSettingsLimitWheelOutlineCheckbox, dkSteeringWheelSettingsWheelMarkerCheckbox, dkSteeringWheelSettingsWheelSpokesCheckbox, dkSteeringWheelSettingsWheelInvertColorCheckbox
	global dkSteeringWheelSettingsWheelSettingsWheelSizeLabel, dkSteeringWheelSettingsWheelSettingsWheelSizeLabelActual, dkSteeringWheelSettingsWheelSettingsWheelSizeIncrease, dkSteeringWheelSettingsWheelSettingsWheelSizeDecrease
	global dkSteeringWheelSettingsWheelSettingsMaxSpeedLabel, dkSteeringWheelSettingsWheelSettingsMaxSpeedLabelActual, dkSteeringWheelSettingsWheelSettingsMaxSpeedIncrease, dkSteeringWheelSettingsWheelSettingsMaxSpeedDecrease
	global dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerLabel, dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerLabelActual, dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerIncrease, dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerDecrease
	global dkSteeringWheelSettingsWheelSettingsMaxDegreesLabel, dkSteeringWheelSettingsWheelSettingsMaxDegreesLabelActual, dkSteeringWheelSettingsWheelSettingsMaxDegreesIncrease, dkSteeringWheelSettingsWheelSettingsMaxDegreesDecrease
	global dkSteeringWheelSettingsWheelSettingsSpokesWidthLabel, dkSteeringWheelSettingsWheelSettingsSpokesWidthLabelActual, dkSteeringWheelSettingsWheelSettingsSpokesWidthIncrease, dkSteeringWheelSettingsWheelSettingsSpokesWidthDecrease

	ac.setVisible(dkSteeringWheelConfigBackground, state)
	ac.setVisible(dkSteeringWheelSettingsConfigLabel, state)

	ac.setVisible(dkSteeringWheelSettingsOnlyOffCenterCheckbox, state)
	ac.setVisible(dkSteeringWheelSettingsBlinkCheckbox, state)
	ac.setVisible(dkSteeringWheelSettingsPaintRedCheckbox, state)
	ac.setVisible(dkSteeringWheelSettingsLimitWheelAngleCheckbox, state)
	ac.setVisible(dkSteeringWheelSettingsLimitWheelOutlineCheckbox, state)
	ac.setVisible(dkSteeringWheelSettingsWheelMarkerCheckbox, state)
	ac.setVisible(dkSteeringWheelSettingsWheelSpokesCheckbox, state)
	ac.setVisible(dkSteeringWheelSettingsWheelInvertColorCheckbox, state)

	ac.setVisible(dkSteeringWheelSettingsWheelSettingsWheelSizeLabel, state)
	ac.setVisible(dkSteeringWheelSettingsWheelSettingsWheelSizeLabelActual, state)
	ac.setVisible(dkSteeringWheelSettingsWheelSettingsWheelSizeIncrease, state)
	ac.setVisible(dkSteeringWheelSettingsWheelSettingsWheelSizeDecrease, state)

	ac.setVisible(dkSteeringWheelSettingsWheelSettingsMaxSpeedLabel, state)
	ac.setVisible(dkSteeringWheelSettingsWheelSettingsMaxSpeedLabelActual, state)
	ac.setVisible(dkSteeringWheelSettingsWheelSettingsMaxSpeedIncrease, state)
	ac.setVisible(dkSteeringWheelSettingsWheelSettingsMaxSpeedDecrease, state)

	ac.setVisible(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerLabel, state)
	ac.setVisible(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerLabelActual, state)
	ac.setVisible(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerIncrease, state)
	ac.setVisible(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerDecrease, state)

	ac.setVisible(dkSteeringWheelSettingsWheelSettingsMaxDegreesLabel, state)
	ac.setVisible(dkSteeringWheelSettingsWheelSettingsMaxDegreesLabelActual, state)
	ac.setVisible(dkSteeringWheelSettingsWheelSettingsMaxDegreesIncrease, state)
	ac.setVisible(dkSteeringWheelSettingsWheelSettingsMaxDegreesDecrease, state)

	ac.setVisible(dkSteeringWheelSettingsWheelSettingsSpokesWidthLabel, state)
	ac.setVisible(dkSteeringWheelSettingsWheelSettingsSpokesWidthLabelActual, state)
	ac.setVisible(dkSteeringWheelSettingsWheelSettingsSpokesWidthIncrease, state)
	ac.setVisible(dkSteeringWheelSettingsWheelSettingsSpokesWidthDecrease, state)

def dkSteeringWheelSettingsDoOnlyOffCenterCheckbox(name, state):
	global app, dkSteeringWheelSettingsOnlyOffCenter
	if state == 1:
		dkCH.rc(app, app, 'onlyoffcenter', "True", 1)
		dkSteeringWheelSettingsOnlyOffCenter = True
	else:
		dkCH.rc(app, app, 'onlyoffcenter', "False", 1)
		dkSteeringWheelSettingsOnlyOffCenter = False

def dkSteeringWheelSettingsDoBlinkCheckbox(name, state):
	global app, dkSteeringWheelSettingsBlink
	if state == 1:
		dkCH.rc(app, app, 'blink', "True", 1)
		dkSteeringWheelSettingsBlink = True
	else:
		dkCH.rc(app, app, 'blink', "False", 1)
		dkSteeringWheelSettingsBlink = False

def dkSteeringWheelSettingsDoPaintRedCheckbox(name, state):
	global app, dkSteeringWheelSettingsPaintRed
	if state == 1:
		dkCH.rc(app, app, 'paintred', "True", 1)
		dkSteeringWheelSettingsPaintRed = True
	else:
		dkCH.rc(app, app, 'paintred', "False", 1)
		dkSteeringWheelSettingsPaintRed = False

def dkSteeringWheelSettingsDoLimitWheelAngleCheckbox(name, state):
	global app, dkSteeringWheelSettingsLimitWheelAngle
	if state == 1:
		dkCH.rc(app, app, 'limitwheelangle', "True", 1)
		dkSteeringWheelSettingsLimitWheelAngle = True
	else:
		dkCH.rc(app, app, 'limitwheelangle', "False", 1)
		dkSteeringWheelSettingsLimitWheelAngle = False

def dkSteeringWheelSettingsDoLimitWheelOutlineCheckbox(name, state):
	global app, dkSteeringWheelSettingsOutline
	if state == 1:
		dkCH.rc(app, app, 'outline', "True", 1)
		dkSteeringWheelSettingsOutline = True
	else:
		dkCH.rc(app, app, 'outline', "False", 1)
		dkSteeringWheelSettingsOutline = False

def dkSteeringWheelSettingsDoWheelMarkerCheckbox(name, state):
	global app, dkSteeringWheelSettingsMarker
	if state == 1:
		dkCH.rc(app, app, 'marker', "True", 1)
		dkSteeringWheelSettingsMarker = True
	else:
		dkCH.rc(app, app, 'marker', "False", 1)
		dkSteeringWheelSettingsMarker = False

def dkSteeringWheelSettingsDoWheelSpokesCheckbox(name, state):
	global app, dkSteeringWheelSettingsSpokes
	if state == 1:
		dkCH.rc(app, app, 'spokes', "True", 1)
		dkSteeringWheelSettingsSpokes = True
	else:
		dkCH.rc(app, app, 'spokes', "False", 1)
		dkSteeringWheelSettingsSpokes = False

def dkSteeringWheelSettingsDoWheelInvertColorCheckbox(name, state):
	global app, dkSteeringWheelSettingsInvertWheelColor
	if state == 1:
		dkCH.rc(app, app, 'invertwheelcolor', "True", 1)
		dkSteeringWheelSettingsInvertWheelColor = True
	else:
		dkCH.rc(app, app, 'invertwheelcolor', "False", 1)
		dkSteeringWheelSettingsInvertWheelColor = False

def dkSteeringWheelSettingsDoWheelSettingsWheelSizeIncrease(name, state):
	global app, dkSteeringWheelSettingsAppWidth, dkSteeringWheelSettingsWheelSettingsWheelSizeLabelActual
	if dkSteeringWheelSettingsAppWidth < 500:
		dkSteeringWheelSettingsAppWidth += 5
		ac.setText(dkSteeringWheelSettingsWheelSettingsWheelSizeLabelActual, "("+str(dkSteeringWheelSettingsAppWidth)+")")
		dkCH.rc(app, app, 'appsize', dkSteeringWheelSettingsAppWidth, 1)

def dkSteeringWheelSettingsDoWheelSettingsWheelSizeDecrease(name, state):
	global app, dkSteeringWheelSettingsAppWidth, dkSteeringWheelSettingsWheelSettingsWheelSizeLabelActual
	if dkSteeringWheelSettingsAppWidth > 20:
		dkSteeringWheelSettingsAppWidth -= 5
		ac.setText(dkSteeringWheelSettingsWheelSettingsWheelSizeLabelActual, "("+str(dkSteeringWheelSettingsAppWidth)+")")
		dkCH.rc(app, app, 'appsize', dkSteeringWheelSettingsAppWidth, 1)

def dkSteeringWheelSettingsDoWheelSettingsMaxSpeedIncrease(name, state):
	global app, dkSteeringWheelSettingsMaxSpeed, dkSteeringWheelSettingsWheelSettingsMaxSpeedLabelActual
	if dkSteeringWheelSettingsMaxSpeed >= 400 and dkSteeringWheelSettingsMaxSpeed <= 1000:
		dkSteeringWheelSettingsMaxSpeed += 10
		if dkSteeringWheelSettingsMaxSpeed > 1000:
			dkSteeringWheelSettingsMaxSpeed = 1000
		ac.setText(dkSteeringWheelSettingsWheelSettingsMaxSpeedLabelActual, "("+str(dkSteeringWheelSettingsMaxSpeed)+")")
		dkCH.rc(app, app, 'maxspeed', dkSteeringWheelSettingsMaxSpeed, 1)
	if dkSteeringWheelSettingsMaxSpeed >= 50 and dkSteeringWheelSettingsMaxSpeed < 400:
		dkSteeringWheelSettingsMaxSpeed += 5
		ac.setText(dkSteeringWheelSettingsWheelSettingsMaxSpeedLabelActual, "("+str(dkSteeringWheelSettingsMaxSpeed)+")")
		dkCH.rc(app, app, 'maxspeed', dkSteeringWheelSettingsMaxSpeed, 1)
	if dkSteeringWheelSettingsMaxSpeed >= 0 and dkSteeringWheelSettingsMaxSpeed < 50:
		dkSteeringWheelSettingsMaxSpeed += 1
		ac.setText(dkSteeringWheelSettingsWheelSettingsMaxSpeedLabelActual, "("+str(dkSteeringWheelSettingsMaxSpeed)+")")
		dkCH.rc(app, app, 'maxspeed', dkSteeringWheelSettingsMaxSpeed, 1)

def dkSteeringWheelSettingsDoWheelSettingsMaxSpeedDecrease(name, state):
	global app, dkSteeringWheelSettingsMaxSpeed, dkSteeringWheelSettingsWheelSettingsMaxSpeedLabelActual
	if dkSteeringWheelSettingsMaxSpeed >= 400 and dkSteeringWheelSettingsMaxSpeed <= 1000:
		dkSteeringWheelSettingsMaxSpeed -= 10
		ac.setText(dkSteeringWheelSettingsWheelSettingsMaxSpeedLabelActual, "("+str(dkSteeringWheelSettingsMaxSpeed)+")")
		dkCH.rc(app, app, 'maxspeed', dkSteeringWheelSettingsMaxSpeed, 1)
	if dkSteeringWheelSettingsMaxSpeed >= 50 and dkSteeringWheelSettingsMaxSpeed < 400:
		dkSteeringWheelSettingsMaxSpeed -= 5
		ac.setText(dkSteeringWheelSettingsWheelSettingsMaxSpeedLabelActual, "("+str(dkSteeringWheelSettingsMaxSpeed)+")")
		dkCH.rc(app, app, 'maxspeed', dkSteeringWheelSettingsMaxSpeed, 1)
	if dkSteeringWheelSettingsMaxSpeed >= 0 and dkSteeringWheelSettingsMaxSpeed < 50:
		dkSteeringWheelSettingsMaxSpeed -= 1
		if dkSteeringWheelSettingsMaxSpeed < 0:
			dkSteeringWheelSettingsMaxSpeed = 0
		ac.setText(dkSteeringWheelSettingsWheelSettingsMaxSpeedLabelActual, "("+str(dkSteeringWheelSettingsMaxSpeed)+")")
		dkCH.rc(app, app, 'maxspeed', dkSteeringWheelSettingsMaxSpeed, 1)

def dkSteeringWheelSettingsDoWheelSettingsMaxSpeedMarkerIncrease(name, state):
	global app, dkSteeringWheelSettingsMarkerTopSpeed, dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerLabelActual
	if dkSteeringWheelSettingsMarkerTopSpeed >= 400 and dkSteeringWheelSettingsMarkerTopSpeed <= 1000:
		dkSteeringWheelSettingsMarkerTopSpeed += 10
		if dkSteeringWheelSettingsMarkerTopSpeed > 1000:
			dkSteeringWheelSettingsMarkerTopSpeed = 1000
		ac.setText(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerLabelActual, "("+str(dkSteeringWheelSettingsMarkerTopSpeed)+")")
		dkCH.rc(app, app, 'markertopspeed', dkSteeringWheelSettingsMarkerTopSpeed, 1)
	if dkSteeringWheelSettingsMarkerTopSpeed >= 50 and dkSteeringWheelSettingsMarkerTopSpeed < 400:
		dkSteeringWheelSettingsMarkerTopSpeed += 5
		ac.setText(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerLabelActual, "("+str(dkSteeringWheelSettingsMarkerTopSpeed)+")")
		dkCH.rc(app, app, 'markertopspeed', dkSteeringWheelSettingsMarkerTopSpeed, 1)
	if dkSteeringWheelSettingsMarkerTopSpeed >= 0 and dkSteeringWheelSettingsMarkerTopSpeed < 50:
		dkSteeringWheelSettingsMarkerTopSpeed += 1
		ac.setText(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerLabelActual, "("+str(dkSteeringWheelSettingsMarkerTopSpeed)+")")
		dkCH.rc(app, app, 'markertopspeed', dkSteeringWheelSettingsMarkerTopSpeed, 1)

def dkSteeringWheelSettingsDoWheelSettingsMaxSpeedMarkerDecrease(name, state):
	global app, dkSteeringWheelSettingsMarkerTopSpeed, dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerLabelActual
	if dkSteeringWheelSettingsMarkerTopSpeed >= 400 and dkSteeringWheelSettingsMarkerTopSpeed <= 1000:
		dkSteeringWheelSettingsMarkerTopSpeed -= 10
		ac.setText(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerLabelActual, "("+str(dkSteeringWheelSettingsMarkerTopSpeed)+")")
		dkCH.rc(app, app, 'markertopspeed', dkSteeringWheelSettingsMarkerTopSpeed, 1)
	if dkSteeringWheelSettingsMarkerTopSpeed >= 50 and dkSteeringWheelSettingsMarkerTopSpeed < 400:
		dkSteeringWheelSettingsMarkerTopSpeed -= 5
		ac.setText(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerLabelActual, "("+str(dkSteeringWheelSettingsMarkerTopSpeed)+")")
		dkCH.rc(app, app, 'markertopspeed', dkSteeringWheelSettingsMarkerTopSpeed, 1)
	if dkSteeringWheelSettingsMarkerTopSpeed >= 0 and dkSteeringWheelSettingsMarkerTopSpeed < 50:
		dkSteeringWheelSettingsMarkerTopSpeed -= 1
		if dkSteeringWheelSettingsMarkerTopSpeed < 0:
			dkSteeringWheelSettingsMarkerTopSpeed = 0
		ac.setText(dkSteeringWheelSettingsWheelSettingsMaxSpeedMarkerLabelActual, "("+str(dkSteeringWheelSettingsMarkerTopSpeed)+")")
		dkCH.rc(app, app, 'markertopspeed', dkSteeringWheelSettingsMarkerTopSpeed, 1)

def dkSteeringWheelSettingsDoWheelSettingsMaxDegreesIncrease(name, state):
	global app, dkSteeringWheelSettingsMaxDegrees, dkSteeringWheelSettingsWheelSettingsMaxDegreesLabelActual
	if dkSteeringWheelSettingsMaxDegrees < 1080:
		dkSteeringWheelSettingsMaxDegrees += 10
		if dkSteeringWheelSettingsMaxDegrees > 1080:
			dkSteeringWheelSettingsMaxDegrees = 1080
		ac.setText(dkSteeringWheelSettingsWheelSettingsMaxDegreesLabelActual, "("+str(dkSteeringWheelSettingsMaxDegrees)+")")
		dkCH.rc(app, app, 'maxdegrees', dkSteeringWheelSettingsMaxDegrees, 1)

def dkSteeringWheelSettingsDoWheelSettingsMaxDegreesDecrease(name, state):
	global app, dkSteeringWheelSettingsMaxDegrees, dkSteeringWheelSettingsWheelSettingsMaxDegreesLabelActual
	if dkSteeringWheelSettingsMaxDegrees > 10:
		dkSteeringWheelSettingsMaxDegrees -= 10
		if dkSteeringWheelSettingsMaxDegrees < 10:
			dkSteeringWheelSettingsMaxDegrees = 10
		ac.setText(dkSteeringWheelSettingsWheelSettingsMaxDegreesLabelActual, "("+str(dkSteeringWheelSettingsMaxDegrees)+")")
		dkCH.rc(app, app, 'maxdegrees', dkSteeringWheelSettingsMaxDegrees, 1)

def dkSteeringWheelSettingsDoWheelSettingsSpokesWidthIncrease(name, state):
	global app, dkSteeringWheelSettingsSpokesWidth, dkSteeringWheelSettingsWheelSettingsSpokesWidthLabelActual
	if dkSteeringWheelSettingsSpokesWidth < 60:
		dkSteeringWheelSettingsSpokesWidth += 10
		ac.setText(dkSteeringWheelSettingsWheelSettingsSpokesWidthLabelActual, "("+str(dkSteeringWheelSettingsSpokesWidth)+")")
		dkCH.rc(app, app, 'spokeswidth', dkSteeringWheelSettingsSpokesWidth, 1)

def dkSteeringWheelSettingsDoWheelSettingsSpokesWidthDecrease(name, state):
	global app, dkSteeringWheelSettingsSpokesWidth, dkSteeringWheelSettingsWheelSettingsSpokesWidthLabelActual
	if dkSteeringWheelSettingsSpokesWidth > 20:
		dkSteeringWheelSettingsSpokesWidth -= 10
		ac.setText(dkSteeringWheelSettingsWheelSettingsSpokesWidthLabelActual, "("+str(dkSteeringWheelSettingsSpokesWidth)+")")
		dkCH.rc(app, app, 'spokeswidth', dkSteeringWheelSettingsSpokesWidth, 1)

def setDegreeColor(degreeColorLevel):
	degreeColorLevelAdj=0
	if dkSteeringWheelSettingsInvertWheelColor:
		# light
		if degreeColorLevel==0:
			ac.glColor4f(1.0, 1.0, 1.0, 0.3)
		else:
			degreeColorLevelAdj=0.5+degreeColorLevel*0.5
			ac.glColor4f(0.5+0.5*degreeColorLevel, 1*(1-degreeColorLevel*1.5), 0, 0.3+0.3*(degreeColorLevel))
	else:
		# dark
		if degreeColorLevel==0:
			ac.glColor4f(0.1, 0.1, 0.1, 0.7)
		else:
			ac.glColor4f(0.5+0.5*degreeColorLevel, 1*(1-degreeColorLevel*1.5), 0, 0.7)

def onFormRender(deltaT):
	global appWindow, dkSteeringWheelConfigButtonTimer, dkSteeringWheelConfigButton, configWindowVisible

	ac.setBackgroundOpacity(appWindow, dkSteeringWheelSettingsBackgroundOpacity)

	# Handle configuration window
	if dkSteeringWheelConfigButtonTimer > 0 and configWindowVisible == False:
		if (time.clock() - dkSteeringWheelConfigButtonTimer) > 3:
			dkSteeringWheelConfigButtonTimer = 0
			ac.setVisible(dkSteeringWheelConfigButton, 0)

	drawWheel = False

	wheel_center_x = dkSteeringWheelSettingsAppWidth * 0.5
	wheel_center_y = appHeight - wheel_center_x
	wheel_out_radius = wheel_center_x * 0.76
	wheel_in_radius = wheel_center_x * 0.6
	wheel_out_radiusO = wheel_center_x * 0.78
	wheel_in_radiusO = wheel_center_x * 0.58
	marker_width = 10
	center_radius = wheel_center_x * 0.15

	# This stops the virtual wheel from spinning too far, so you can 
	# always tell which direction you need to turn to get back to center
	degreesMin = -dkSteeringWheelSettingsMaxDegrees
	degreesMax = dkSteeringWheelSettingsMaxDegrees

	carActive = 0
	carActive = ac.getFocusedCar()
	degrees = ac.getCarState(carActive, acsys.CS.Steer)
	SpeedKMH = ac.getCarState(carActive, acsys.CS.SpeedKMH)
	showRed = False
	blinkOn = False
	redPaint = False
	
	if dkSteeringWheelSettingsPaintRed:
		redPaint = True

	if (degrees < -10 or degrees > 10) and SpeedKMH < 1:
		showRed = True

	if dkSteeringWheelSettingsLimitWheelAngle:
		if degrees < degreesMin:
			degrees = degreesMin
		if degrees > degreesMax:
			degrees = degreesMax

	degreesDisp = degrees - 90

	if dkSteeringWheelSettingsBlink:
		redPaint = False
		if int(round(time.time() * 10) %10) < 5:
			blinkOn = True

	# Only draw wheel if not centered
	if SpeedKMH < 2 and dkSteeringWheelSettingsOnlyOffCenter and showRed:
		drawWheel = True

	# if the speed is greater than dkSteeringWheelSettingsMaxSpeed then draw nothing
	if SpeedKMH < dkSteeringWheelSettingsMaxSpeed and dkSteeringWheelSettingsOnlyOffCenter != True:
		drawWheel = True
		
	if drawWheel:
		# ac.console("De:"+str(degrees))
		# Paint wheel
		degreeColorAngleDiff = 0
		for i in range(0, 360, 10): #360 is not included

			# Paint steering wheel outline
			if dkSteeringWheelSettingsOutline:
				ac.glBegin(3)
				if dkSteeringWheelSettingsInvertWheelColor:
					ac.glColor4f(0.0, 0.0, 0.0, 0.2)
				else:
					ac.glColor4f(1.0, 1.0, 1.0, 0.2)
				ac.glVertex2f(wheel_center_x + math.cos(math.radians(i+10))*wheel_out_radiusO,wheel_center_y + math.sin(math.radians(i+10))*wheel_out_radiusO)
				ac.glVertex2f(wheel_center_x + math.cos(math.radians(i))*wheel_out_radiusO,wheel_center_y + math.sin(math.radians(i))*wheel_out_radiusO)
				ac.glVertex2f(wheel_center_x + math.cos(math.radians(i))*wheel_out_radius,wheel_center_y + math.sin(math.radians(i))*wheel_out_radius)
				ac.glVertex2f(wheel_center_x + math.cos(math.radians(i+10))*wheel_out_radius,wheel_center_y + math.sin(math.radians(i+10))*wheel_out_radius)
				ac.glVertex2f(wheel_center_x + math.cos(math.radians(i+10))*wheel_in_radius,wheel_center_y + math.sin(math.radians(i+10))*wheel_in_radius)
				ac.glVertex2f(wheel_center_x + math.cos(math.radians(i))*wheel_in_radius,wheel_center_y + math.sin(math.radians(i))*wheel_in_radius)
				ac.glVertex2f(wheel_center_x + math.cos(math.radians(i))*wheel_in_radiusO,wheel_center_y + math.sin(math.radians(i))*wheel_in_radiusO)
				ac.glVertex2f(wheel_center_x + math.cos(math.radians(i+10))*wheel_in_radiusO,wheel_center_y + math.sin(math.radians(i+10))*wheel_in_radiusO)
				ac.glEnd()

			# Paint steering wheel
			degreeColorLevel=0
			degreeColorLevelAdj=0
			degreeColorLevelLast=0
			degreeColorAngleDiffNext=0
			ac.glBegin(3)
			if showRed and redPaint:
				ac.glColor4f(1.0, 0.0, 0.0, 0.3)
			elif showRed and blinkOn:
				ac.glColor4f(1.0, 0.0, 0.0, 0.3)
			else:
				# Turn Right
				if degrees >= marker_width/5:
					if degrees > i:
						degreeColorLevel = (i+10)/(degreesMax/2)
						# check the last color block
						if i+10 > degrees: 
							degreeColorAngleDiffNext = degrees-i
						# over 360
						if degrees >= 360 and i <= degrees-360:
							degreeColorLevel = (i+10+360)/(degreesMax/2)
							if i+10 > degrees-360:
								degreeColorAngleDiffNext = (degrees-360)-i
						# deal with first block when steer at last postion
						if i==0 and degrees > 350 and degrees <360:
							degreeColorAngleDiff = degrees-350
							#ac.console("DD:"+str(degrees)+" i:"+str(i)+" DF:"+str(degreeColorAngleDiff)+str(i)+" LV:"+str(degreeColorLevel))
				# Turn Left
				elif -degrees >= marker_width/5: 
					if -degrees > (340-i):
						degreeColorLevel = (360-i)/(degreesMax/2)
						# check the 2nd last color block (the last always fill)
						if (350-i) > -degrees: 
							# ac.console("Skip:"+str(i)+" DD:"+str(degrees))
							degreeColorAngleDiff = degrees+(340-i)
						# over 360
						if -degrees >= 360 and (-degrees-360) > (340-i):
							degreeColorLevel = (360+360-i)/(degreesMax/2)
							if  (-degrees-360) < (350-i):
								# ac.console("Skip:"+str(i)+" DD:"+str(degrees))
								degreeColorAngleDiff = degrees+360+(340-i)
						if i==350 and -degrees > 350 and -degrees <360:
							degreeColorAngleDiff = degrees+350
							#ac.console("DD:"+str(degrees)+" i:"+str(i)+" DF:"+str(degreeColorAngleDiff)+str(i)+" LV:"+str(degreeColorLevel))

				# draw a full block
				if degreeColorAngleDiff == 0: #draw color blocks flow wheel mark
					setDegreeColor(degreeColorLevel)
					i9 = i-90
					ac.glVertex2f(wheel_center_x + math.cos(math.radians(i9+10))*wheel_out_radius,wheel_center_y + math.sin(math.radians(i9+10))*wheel_out_radius)
					ac.glVertex2f(wheel_center_x + math.cos(math.radians(i9))*wheel_out_radius,wheel_center_y + math.sin(math.radians(i9))*wheel_out_radius)
					ac.glVertex2f(wheel_center_x + math.cos(math.radians(i9))*wheel_in_radius,wheel_center_y + math.sin(math.radians(i9))*wheel_in_radius)
					ac.glVertex2f(wheel_center_x + math.cos(math.radians(i9+10))*wheel_in_radius,wheel_center_y + math.sin(math.radians(i9+10))*wheel_in_radius)
					#ac.console("DD:"+str(degrees)+" i:"+str(i)+" LV:"+str(degreeColorLevel))
				else: # draw 2 color blocks to quickly flow wheel mark
					neg = degreeColorAngleDiff/abs(degreeColorAngleDiff)
					if degrees>=0: #turn right
						degreeColorLevelFar = degreeColorLevel
						degreeColorLevelNear = (i+10)/(degreesMax/2)
						if degrees >= 350:
							degreeColorLevelNear = (i+10+360)/(degreesMax/2)
					else: #turn left
						degreeColorLevelFar = 0
						degreeColorLevelNear = degreeColorLevel
						if -degrees >= 350:
							degreeColorLevelFar = (360-i)/(degreesMax/2)
							if i==350:
								degreeColorLevelNear= (360+360-i)/(degreesMax/2)
					# ac.console("DD:"+str(degrees)+" i:"+str(i)+" Near:"+str(degreeColorLevelNear)+" Far:"+str(degreeColorLevelFar))
					# far color block (<360:steer color, >360:first loop color)
					setDegreeColor(degreeColorLevelFar)
					degreesStart = degreesDisp+marker_width*neg
					degreesEnd = degreesStart+(10*neg-degreeColorAngleDiff)
					#ac.console("DD:"+str(degreesDisp)+" DF:"+str(degreeColorAngleDiff)+" DS:"+str(degreesStart)+" DE:"+str(degreesEnd))
					if degreesStart < degreesEnd:
						ac.glVertex2f(wheel_center_x + math.cos(math.radians(degreesEnd))*wheel_out_radius, wheel_center_y + math.sin(math.radians(degreesEnd))*wheel_out_radius)
						ac.glVertex2f(wheel_center_x + math.cos(math.radians(degreesStart))*wheel_out_radius, wheel_center_y + math.sin(math.radians(degreesStart))*wheel_out_radius)
						ac.glVertex2f(wheel_center_x + math.cos(math.radians(degreesStart))*wheel_in_radius, wheel_center_y + math.sin(math.radians(degreesStart))*wheel_in_radius)
						ac.glVertex2f(wheel_center_x + math.cos(math.radians(degreesEnd))*wheel_in_radius, wheel_center_y + math.sin(math.radians(degreesEnd))*wheel_in_radius)
					else:
						ac.glVertex2f(wheel_center_x + math.cos(math.radians(degreesStart))*wheel_out_radius, wheel_center_y + math.sin(math.radians(degreesStart))*wheel_out_radius)
						ac.glVertex2f(wheel_center_x + math.cos(math.radians(degreesEnd))*wheel_out_radius, wheel_center_y + math.sin(math.radians(degreesEnd))*wheel_out_radius)
						ac.glVertex2f(wheel_center_x + math.cos(math.radians(degreesEnd))*wheel_in_radius, wheel_center_y + math.sin(math.radians(degreesEnd))*wheel_in_radius)
						ac.glVertex2f(wheel_center_x + math.cos(math.radians(degreesStart))*wheel_in_radius, wheel_center_y + math.sin(math.radians(degreesStart))*wheel_in_radius)

					# Near color block (highlight red)
					setDegreeColor(degreeColorLevelNear)
					# ac.console("Near:"+str(degreeColorLevel))
					#ac.glColor4f(1,1,0,0.5)
					degreesStart = degreesDisp+marker_width*neg
					degreesEnd = degreesStart-degreeColorAngleDiff
					#ac.console("DD:"+str(degreesDisp)+" DF:"+str(degreeColorAngleDiff)+" DS:"+str(degreesStart)+" DE:"+str(degreesEnd))
					if degreesStart < degreesEnd:
						ac.glVertex2f(wheel_center_x + math.cos(math.radians(degreesEnd))*wheel_out_radius, wheel_center_y + math.sin(math.radians(degreesEnd))*wheel_out_radius)
						ac.glVertex2f(wheel_center_x + math.cos(math.radians(degreesStart))*wheel_out_radius, wheel_center_y + math.sin(math.radians(degreesStart))*wheel_out_radius)
						ac.glVertex2f(wheel_center_x + math.cos(math.radians(degreesStart))*wheel_in_radius, wheel_center_y + math.sin(math.radians(degreesStart))*wheel_in_radius)
						ac.glVertex2f(wheel_center_x + math.cos(math.radians(degreesEnd))*wheel_in_radius, wheel_center_y + math.sin(math.radians(degreesEnd))*wheel_in_radius)
					else:
						ac.glVertex2f(wheel_center_x + math.cos(math.radians(degreesStart))*wheel_out_radius, wheel_center_y + math.sin(math.radians(degreesStart))*wheel_out_radius)
						ac.glVertex2f(wheel_center_x + math.cos(math.radians(degreesEnd))*wheel_out_radius, wheel_center_y + math.sin(math.radians(degreesEnd))*wheel_out_radius)
						ac.glVertex2f(wheel_center_x + math.cos(math.radians(degreesEnd))*wheel_in_radius, wheel_center_y + math.sin(math.radians(degreesEnd))*wheel_in_radius)
						ac.glVertex2f(wheel_center_x + math.cos(math.radians(degreesStart))*wheel_in_radius, wheel_center_y + math.sin(math.radians(degreesStart))*wheel_in_radius)

					degreeColorAngleDiff=0


				if degreeColorAngleDiffNext != 0:
					degreeColorAngleDiff=degreeColorAngleDiffNext
					degreeColorLevelLast=degreeColorLevel


			ac.glEnd()

		# Paint steering wheel spokes and center
		if dkSteeringWheelSettingsSpokes:
			if dkSteeringWheelSettingsOutline:
				# Paint steering wheel spokes and center outline
				ac.glBegin(3)
				if dkSteeringWheelSettingsInvertWheelColor:
					ac.glColor4f(1.0, 1.0, 1.0, 0.2)
				else:
					ac.glColor4f(0.0, 0.0, 0.0, 0.2)
				wAdd = 1.35 # Add outline width
				for i in [80, 180, 280]:
					ac.glVertex2f(wheel_center_x + math.cos(math.radians(i+degreesDisp+(dkSteeringWheelSettingsSpokesWidth*wAdd)/12))*wheel_in_radius, wheel_center_y + math.sin(math.radians(i+degreesDisp+(dkSteeringWheelSettingsSpokesWidth*wAdd)/12))*wheel_in_radius)
					ac.glVertex2f(wheel_center_x + math.cos(math.radians(i+degreesDisp-(dkSteeringWheelSettingsSpokesWidth*wAdd)/12))*wheel_in_radius, wheel_center_y + math.sin(math.radians(i+degreesDisp-(dkSteeringWheelSettingsSpokesWidth*wAdd)/12))*wheel_in_radius)
					ac.glVertex2f(wheel_center_x + math.cos(math.radians(i+degreesDisp-(dkSteeringWheelSettingsSpokesWidth*wAdd)))*center_radius, wheel_center_y + math.sin(math.radians(i+degreesDisp-(dkSteeringWheelSettingsSpokesWidth*wAdd)))*center_radius)
					ac.glVertex2f(wheel_center_x + math.cos(math.radians(i+degreesDisp+(dkSteeringWheelSettingsSpokesWidth*wAdd)))*center_radius, wheel_center_y + math.sin(math.radians(i+degreesDisp+(dkSteeringWheelSettingsSpokesWidth*wAdd)))*center_radius)
				ac.glEnd()

			# Paint steering wheel spokes
			ac.glBegin(3)
			if dkSteeringWheelSettingsInvertWheelColor:
				ac.glColor4f(0.2, 0.2, 0.2, 0.8)
			else:
				ac.glColor4f(0.5, 0.5, 0.5, 0.8)
			for i in [80, 180, 280]:
				ac.glVertex2f(wheel_center_x + math.cos(math.radians(i+degreesDisp+dkSteeringWheelSettingsSpokesWidth/12))*wheel_in_radius, wheel_center_y + math.sin(math.radians(i+degreesDisp+dkSteeringWheelSettingsSpokesWidth/12))*wheel_in_radius)
				ac.glVertex2f(wheel_center_x + math.cos(math.radians(i+degreesDisp-dkSteeringWheelSettingsSpokesWidth/12))*wheel_in_radius, wheel_center_y + math.sin(math.radians(i+degreesDisp-dkSteeringWheelSettingsSpokesWidth/12))*wheel_in_radius)
				ac.glVertex2f(wheel_center_x + math.cos(math.radians(i+degreesDisp-dkSteeringWheelSettingsSpokesWidth))*center_radius, wheel_center_y + math.sin(math.radians(i+degreesDisp-dkSteeringWheelSettingsSpokesWidth))*center_radius)
				ac.glVertex2f(wheel_center_x + math.cos(math.radians(i+degreesDisp+dkSteeringWheelSettingsSpokesWidth))*center_radius, wheel_center_y + math.sin(math.radians(i+degreesDisp+dkSteeringWheelSettingsSpokesWidth))*center_radius)
			ac.glEnd()
			# Paint steering wheel center
			for i in range(0, 360, 10):
				ac.glBegin(3)
				if dkSteeringWheelSettingsInvertWheelColor:
					ac.glColor4f(0.1, 0.1, 0.1, 1)
				else:
					ac.glColor4f(0.3, 0.3, 0.3, 1)
				ac.glVertex2f(wheel_center_x + math.cos(math.radians(i+10))*center_radius, wheel_center_y + math.sin(math.radians(i+10))*center_radius)
				ac.glVertex2f(wheel_center_x + math.cos(math.radians(i))*center_radius, wheel_center_y + math.sin(math.radians(i))*center_radius)
				ac.glVertex2f(wheel_center_x, wheel_center_y)
				ac.glVertex2f(wheel_center_x, wheel_center_y)
				ac.glEnd()

		# Paint steering wheel center marker if speed is less than dkSteeringWheelSettingsMarkerTopSpeed
		if dkSteeringWheelSettingsMarker and SpeedKMH < dkSteeringWheelSettingsMarkerTopSpeed:

			########### Right part
			ac.glBegin(3)
			if showRed and redPaint:
				ac.glColor4f(1.0, 0.0, 0.0, 0.3)
			elif showRed and blinkOn:
				ac.glColor4f(1.0, 0.0, 0.0, 0.3)
			else:
				if dkSteeringWheelSettingsInvertWheelColor:
					ac.glColor4f(0.1, 0.1, 0.1, 0.3)
				else:
					ac.glColor4f(1.0, 1.0, 1.0, 0.3)
			ac.glVertex2f(wheel_center_x + math.cos(math.radians(degreesDisp+marker_width))*wheel_out_radius, wheel_center_y + math.sin(math.radians(degreesDisp+marker_width))*wheel_out_radius)
			ac.glVertex2f(wheel_center_x + math.cos(math.radians(degreesDisp))*wheel_out_radius, wheel_center_y + math.sin(math.radians(degreesDisp))*wheel_out_radius)
			ac.glVertex2f(wheel_center_x + math.cos(math.radians(degreesDisp))*wheel_in_radius, wheel_center_y + math.sin(math.radians(degreesDisp))*wheel_in_radius)
			ac.glVertex2f(wheel_center_x + math.cos(math.radians(degreesDisp+marker_width))*wheel_in_radius, wheel_center_y + math.sin(math.radians(degreesDisp+marker_width))*wheel_in_radius)
			ac.glEnd()

			########### Left part
			ac.glBegin(3)
			if showRed and redPaint:
				ac.glColor4f(1.0, 0.0, 0.0, 0.3)
			elif showRed and blinkOn:
				ac.glColor4f(1.0, 0.0, 0.0, 0.3)
			else:
				if dkSteeringWheelSettingsInvertWheelColor:
					ac.glColor4f(0.1, 0.1, 0.1, 0.3)
				else:
					ac.glColor4f(1.0, 1.0, 1.0, 0.3)
			ac.glVertex2f(wheel_center_x + math.cos(math.radians(degreesDisp))*wheel_out_radius, wheel_center_y + math.sin(math.radians(degreesDisp))*wheel_out_radius)
			ac.glVertex2f(wheel_center_x + math.cos(math.radians(degreesDisp-marker_width))*wheel_out_radius, wheel_center_y + math.sin(math.radians(degreesDisp-marker_width))*wheel_out_radius)
			ac.glVertex2f(wheel_center_x + math.cos(math.radians(degreesDisp-marker_width))*wheel_in_radius, wheel_center_y + math.sin(math.radians(degreesDisp-marker_width))*wheel_in_radius)
			ac.glVertex2f(wheel_center_x + math.cos(math.radians(degreesDisp))*wheel_in_radius, wheel_center_y + math.sin(math.radians(degreesDisp))*wheel_in_radius)
			ac.glEnd()
