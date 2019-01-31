#!/usr/bin/env python3

'''
Developer:
Nathan Ahrens
1/11/2019
Ashland University Office of Information Technology

Description:
Use this script to interface with the Jamf Cloud instance and manage mobile apps.
Requires "requests" to be installed (pip3 install requests)
Requires that the following values are in the user's environment variables:
JSS_USER=[jamf username]
JSS_PASSWORD=[jamf password] - encode it using base64.b64encode("password")
JSS_URL = "https://yourcompany.jamfcloud.com"

Jamf API Documentation:
UAPI
https://yourcompany.jamfcloud.com/uapi/doc/
Classic API
https://developer.jamf.com/apis/classic-api/index
'''

import requests
import json
import base64
import os

requests.packages.urllib3.disable_warnings()

#
# Returns the entire list of mobile groups (static and smart) in the jamf instance.
#
def getMobileGroups():
    token = base64.b64encode( (os.environ['JSS_USER'] + ":" + base64.b64decode(os.environ['JSS_PASSWORD'].encode('utf-8')).decode('utf-8') ).encode('utf-8') ).decode('utf-8')
    url = "/JSSResource/mobiledevicegroups"
    payload = ""
    headers = {
        'Accept': "application/json",
        'Authorization': "Basic " + token
    }
    print("Getting list of mobile device groups...")
    response = requests.request("GET", os.environ['JSS_URL'] + url, data=payload, headers=headers)
    groups = json.loads(response.text)['mobile_device_groups']

    return groups

#
# Returns the entire list of mobile apps in the jamf instance.
#
def getMobileApps():
    token = base64.b64encode( (os.environ['JSS_USER'] + ":" + base64.b64decode(os.environ['JSS_PASSWORD'].encode('utf-8')).decode('utf-8') ).encode('utf-8') ).decode('utf-8')
    url = "/JSSResource/mobiledeviceapplications"
    payload = ""
    headers = {
        'Accept': "application/json",
        'Authorization': "Basic " + token
    }
    print("Getting list of applications...")
    response = requests.request("GET", os.environ['JSS_URL'] + url, data=payload, headers=headers)
    apps = json.loads(response.text)['mobile_device_applications']

    # Get the scopes for each app and append it into the list of apps
    for app in apps:

        print("Getting scope of " + app['name'])
        app['scope'] = getMobileAppScope(app['id'])
    return apps

#
# Get the scope of the specified app
#
def getMobileAppScope(id):
    token = base64.b64encode( (os.environ['JSS_USER'] + ":" + base64.b64decode(os.environ['JSS_PASSWORD'].encode('utf-8')).decode('utf-8') ).encode('utf-8') ).decode('utf-8')
    headers = {
        'Accept': "application/json",
        'Authorization': "Basic " + token
    }
    url = "/JSSResource/mobiledeviceapplications/id/" + str(id) + "/subset/Scope"
    return json.loads(requests.request("GET",os.environ['JSS_URL'] + url, data="", headers=headers).text)['mobile_device_application']['scope']
#
# Returns the entire list of mobile devices in the jamf instance.
#
def getMobileDevices():
    token = base64.b64encode( (os.environ['JSS_USER'] + ":" + base64.b64decode(os.environ['JSS_PASSWORD'].encode('utf-8')).decode('utf-8') ).encode('utf-8') ).decode('utf-8')
    url = "/JSSResource/mobiledevices"
    payload = ""
    headers = {
        'Accept': "application/json",
        'Authorization': "Basic " + token
    }
    print("Getting list of mobile devices...")
    response = requests.request("GET", os.environ['JSS_URL'] + url, data=payload, headers=headers)
    devices = json.loads(response.text)['mobile_devices']

    return devices

#
# Edits the app specified by app_id to use the scope provided by scope.
# The parameter scope should be in json format.
#
def applyScopeToApp(scope, app_id):

    url = "/JSSResource/mobiledeviceapplications/id/" + str(app_id)
    token = base64.b64encode( (os.environ['JSS_USER'] + ":" + base64.b64decode(os.environ['JSS_PASSWORD'].encode('utf-8')).decode('utf-8') ).encode('utf-8') ).decode('utf-8')

    # create lists as needed
    mobileDevices = ""
    mobileDeviceGroups = ""
    buildings = ""
    departments = ""
    jssUsers = ""
    jssUserGroups = ""

    for mobileDevice in scope['mobile_devices']:
        mobileDevices += "<mobile_device><id>" + str(mobileDevice['id']) + "</id></mobile_device>"
    for mobileDeviceGroup in scope['mobile_device_groups']:
        mobileDeviceGroups += "<mobile_device_group><id>" + str(mobileDeviceGroup['id']) + "</id></mobile_device_group>"
    for building in scope['buildings']:
        buildings += "<building><id>" + str(building['id']) + "</id></building>"
    for department in scope['departments']:
        departments += "<department><id>" + str(department['id']) + "</id></department>"
    for user in scope['jss_users']:
        jssUsers += "<user><id>" + str(user['id']) + "</id></user>"
    for userGroup in scope['jss_user_groups']:
        jssUserGroups += "<user_group><id>" + str(userGroup['id']) + "</id></user_group>"

    limUsers = ""
    limUserGroups = ""
    limNetSeg = ""

    for user in scope['limitations']['users']:
        limUsers += "<user><name>" + str(user['name']) + "</name></user>"
    for userGroup in scope['limitations']['user_groups']:
        limUserGroups += "<user_group><name>" + str(userGroup['name']) + "</name></user_group>"
    for netSeg in scope['limitations']['network_segments']:
        limNetSeg += "<network_segment><id>" + str(netSeg['id']) + "</id></network_segment>"

    excDevices = ""
    excBuildings = ""
    excDepartments = ""
    excDeviceGroups = ""
    excUsers = ""
    excUserGroups = ""
    excNetSeg = ""
    excJssUsers = ""
    excJssUserGroups = ""

    for dev in scope['exclusions']['mobile_devices']:
        excDevices += "<mobile_device><id>" + str(dev['id']) + "</id></mobile_device>"
    for building in scope['exclusions']['buildings']:
        excBuildings += "<building><id>" + str(building['id']) + "</id></building>"
    for department in scope['exclusions']['departments']:
        excDepartments += "<department><id>" + str(department['id']) + "</id></department>"
    for devGroup in scope['exclusions']['mobile_device_groups']:
        excDeviceGroups += "<mobile_device_group><id>" + str(devGroup['id']) + "</id></mobile_device_group>"
    for user in scope['exclusions']['users']:
        excUsers += "<user><name>" + str(user['name']) + "</name></user>"
    for userGroup in scope['exclusions']['user_groups']:
        excUserGroups += "<user_group><name>" + str(userGroup['name']) + "</name></user_group>"
    for netSeg in scope['exclusions']['network_segments']:
        excNetSeg += "<network_segment><id>" + str(netSeg['id']) + "</id></network_segment>"
    for user in scope['exclusions']['jss_users']:
        excJssUsers += "<user><id>" + str(user['id']) + "</id></user>"
    for userGroup in scope['exclusions']['jss_user_groups']:
        excJssUserGroups += "<user_group><id>" + str(userGroup['id']) + "</id></user_group>"

    payload = """<mobile_device_application><scope>
	<all_mobile_devices>%s</all_mobile_devices>
	<all_jss_users>%s</all_jss_users>
	<mobile_devices>%s</mobile_devices>
	<buildings>%s</buildings>
	<departments>%s</departments>
	<mobile_device_groups>%s</mobile_device_groups>
	<jss_users>%s</jss_users>
	<jss_user_groups>%s</jss_user_groups>
	<limitations>
        <users>%s</users>
		<user_groups>%s</user_groups>
		<network_segments>%s</network_segments>
	</limitations>
	<exclusions>
		<mobile_devices>%s</mobile_devices>
		<buildings>%s</buildings>
		<departments>%s</departments>
		<mobile_device_groups>%s</mobile_device_groups>
		<users>%s</users>
		<user_groups>%s</user_groups>
		<network_segments>%s</network_segments>
		<jss_users>%s</jss_users>
		<jss_user_groups>%s</jss_user_groups>
	</exclusions>
</scope></mobile_device_application>""" % (json.dumps(scope['all_mobile_devices']), json.dumps(scope['all_jss_users']), mobileDevices,
                buildings, departments, mobileDeviceGroups, jssUsers,
                jssUserGroups, limUsers, limUserGroups, limNetSeg, excDevices,
                excBuildings, excDepartments, excDeviceGroups, excUsers,
                excUserGroups, excNetSeg, excJssUsers, excJssUserGroups)

    headers = {
        'Accept': "application/json",
        'Authorization': "Basic " + token,
        'Content-Type': "application/xml"
    }

    response = requests.request("PUT", os.environ['JSS_URL'] + url, data=payload, headers=headers)

    return response.status_code

# main() prints out all the scopes of all the applications.
def main():

    apps = getMobileApps()
    for app in apps:
        print(app['display_name'])
        scope = app['scope']

        # INCLUDED in scope
        print("\tInclude:")
        if scope['all_mobile_devices']:
            print("\t\tAll Mobile Devices")
        if scope['all_jss_users']:
            print("\t\tAll JSS Users")
        for device in scope['mobile_devices']:
            print("\t\tDevice: " + device['name'])
        for building in scope['buildings']:
            print("\t\tBuilding: " + building['name'])
        for department in scope['departments']:
            print("\t\tDepartment: " + department['name'])
        for deviceGroup in scope['mobile_device_groups']:
            print("\t\tDevice Group: " + deviceGroup['name'])
        for jssUser in scope['jss_users']:
            print("\t\tJSS User: " + jssUser['name'])
        for jssUserGroup in scope['jss_user_groups']:
            print("\t\tJSS User Group: " + jssUserGroup['name'])

        # LIMITATIONS in scope
        print("\tLimitations:")
        for user in scope['limitations']['users']:
            print("\t\tUser: " + user['name'])
        for userGroup in scope['limitations']['user_groups']:
            print("\t\tUser Group: " + userGroup['name'])
        for networkSegment in scope['limitations']['network_segments']:
            print("\t\tNetwork Segment: " + networkSegment['name'])

        # EXCLUSIONS for scope
        print("\tExclusions:")
        for device in scope['exclusions']['mobile_devices']:
            print("\t\tDevice: " + device['name'])
        for building in scope['exclusions']['buildings']:
            print("\t\tBuilding: " + building['name'])
        for department in scope['exclusions']['departments']:
            print("\t\tDepartment: " + department['name'])
        for deviceGroup in scope['exclusions']['mobile_device_groups']:
            print("\t\tDevice Group: " + deviceGroup['name'])
        for jssUser in scope['exclusions']['jss_users']:
            print("\t\tJSS User: " + jssUser['name'])
        for jssUserGroup in scope['exclusions']['jss_user_groups']:
            print("\t\tJSS User Group: " + jssUserGroup['name'])
        for user in scope['exclusions']['users']:
            print("\t\tUser: " + user['name'])
        for userGroup in scope['exclusions']['user_groups']:
            print("\t\tUser Group: " + userGroup['name'])
        for networkSegment in scope['exclusions']['network_segments']:
            print("\t\tNetwork Segment: " + networkSegment['name'])

if __name__ == "__main__":
    main()
