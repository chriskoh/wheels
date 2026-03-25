######################################################################################
# dkCH.py (dkConfigHandler)
# Dennis Karlsson (dennis@dennis.se)
#
# 2018-09-04	v0.1	First version
# 2018-09-08	v0.2	Option to save settings (mode "u") to current user documents
#						folder "userhome\Documents\Assetto Corsa\apps\{app}".
#						Activating this mode breaks Content Manager support as it
#						only looks in Assetto Corsa steam folder.
# 2020-01-01	v0.3	Added function to save new settings from app.
#
######################################################################################
# Usage:
#	import dkCH
#	app = "dkApp"
#	dkCH.init(app, parentpath)
#	var = dkCH.rc(app, 'mySection', 'mySetting', 'value')
######################################################################################

import ac, os, sys, configparser, inspect
 
def init(app, mode=""):
	global dkAppArray

	# Figure out importer path
	importer = inspect.getframeinfo(inspect.getouterframes(inspect.currentframe())[1][0])[0]

	if mode == "u":
		ac.log("["+app+"][dkConfigHandler] User home mode detected. This mode breaks Content Manager support.")
		configFilePath=os.path.join(os.path.expanduser("~"), "Documents", "Assetto Corsa", "apps", app)
		if not os.path.exists(configFilePath):
			os.makedirs(configFilePath)
		configFile=os.path.join(configFilePath, app+".ini")
	else:
		configFile=os.path.join(os.path.dirname(importer), app+'.ini')

	# Add app to dkConfigHandler app array
	if 'dkAppArray' in globals():
		ac.log("["+app+"][dkConfigHandler] Adding "+app+" ("+configFile+") to existing dkConfigHandler app array.")
	else:
		dkAppArray = []
		ac.log("["+app+"][dkConfigHandler] "+app+" ("+configFile+") is the first app added to dkConfigHandler app array.")

	dkAppArray.append([app, configFile])

def rc(app, section, setting, value, doWrite=0):
	#ac.log("["+app+"][dkConfigHandler] "+str(section)+", "+str(setting)+", "+str(value)+", "+str(doWrite))

	writeConfig = False

	for daa in dkAppArray:
		if daa[0] == app:
			configFile = daa[1]
			break

	try:
		config = configparser.ConfigParser()
		config.read(configFile)

		# Check if section exist and add if missing.
		if config.has_section(section) != True:
			ac.log("["+app+"][dkConfigHandler] Section "+section+" is missing in configuration file. Adding.")
			config.add_section(section)
			writeConfig = True

		if doWrite == 0:
			# Load setting
			try:
				var = config[section][setting]
			except:
				ac.log("["+app+"][dkConfigHandler] Error loading "+section+" "+setting+" setting. Using default value '"+value+"'.")
				config.set(section, setting, str(value))
				writeConfig = True
				var = value
		else:
			# Set new value
			config.set(section, setting, str(value))
			writeConfig = True
			var = value

		# Write changes to configuration file
		if writeConfig == True:
			with open(configFile, 'w') as writeFile:
				config.write(writeFile)
	except:
		ac.log("["+app+"][dkConfigHandler] Could not open configuration file "+configFile+". Broken file?")

	return str(var);
