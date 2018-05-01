<html>
  <body>
    <h1>Ecobee API Python SDK</h1>
    <b>This project provides a simple python interface to interact with the ecobee Web REST API.</b>
    <div>
      <h2>Overview</h2>
      <b>It provides the following functionality</b>
      <ul>
        <li>Manage Tokens Operations like regestering and refreshing</li>
        <li>Format boilerplate api requests.</li>
        <li>Provide simple functions to perform common api operations</li>
      </ul>
    </div>
      

<div>
  <h2>Install Guide</h2>
  <b>Before you begin Register as an ecobee Developer Here https://www.ecobee.com/developers/</b><br>
  <b>Note: lines with $ mean execute this command in bash</b><br>
  
``` bash
Clone the Repository
$ git clone https://github.com/ecobee/python_api_sdk.git

Navigate inside the root directory
$ cd python_api_sdk

Install the Repository
$ pip install .

#Run the interactive enviornment setup note this only works for mac / linux
$ python setup_scripts/env_setup.py
```
</div>

<h2>User Guide</h2>
<div>

  <b>Note: Bolded Lines with >>> mean execute this command in python</b>

  <h3>Adding Users</h3>
  
``` python
>>> # Create an ApiInterface object
>>> from ebapi.api_interface import ApiInterface
>>> interface = ApiInterface()
>>> 
>>> #Add a user
>>> interface.add_user()
Enter the PIN '<4-digit-pin>' into the Add Application window and click Add Application<br>
waiting press enter to continue...
>>> 
```


<h3>Adding an 3rd Party Application</h3>
<ol>
  <li>Navigate to www.ecobee.com and login with you username and password</li>
  <li>My Account (Top right)</li>
  <li>My Apps (Bottom Left)</li>
  <li>Add application (Bottom Left)</li>
  <li>Enter the <4-digit-pin> into the text box</li>
  <li>Click Validate (Bottom Right)</li>
  <li>Click Add Application</li>
</ol>

<b>Return to you python session and press Enter</b><br>
The SDK will have stored access and refresh tokens for the user accout<br>
It will also store a all the thermostats that the user has<br>
</div>
<div>
  <h2>Making Requests</h2>
  Requests are made by sepecifying a method of the ApiInterface Object<br>
  and a 12 digit Thermostat Identifier.<br>
  These can be found on the About My Thermostat (Bottom Right of a Thermostat Page)<br>
  
All Requests Reutrn Dictionaries from the Ecobee API's JSON format.

Reference Documentation: https://www.ecobee.com/home/developer/api/introduction/index.shtml<br>
Object Defitions: https://www.ecobee.com/home/developer/api/documentation/v1/auth/auth-intro.shtml<br>


``` python
>>> # will dispay the Thermostat ID that are stored
>>> thermostat_identifier.show_users()
>>>
>>> #12 digit thermostat ID
>>> thermostat_identifier = "123456789012" 
>>> 
>>> # Return a Dictionary of the thermostats settings
>>> interface.get_settings(thermostat_identifier)
>>> 
```
</div>
</body>
</html>
