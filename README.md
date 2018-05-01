<html>
<body>
<h1>Ecobee API Python SDK</h1>
<div>
This project provides a simple python interface to interact with the ecobee Web REST API.
</div>
<div>
<h2>Overview</h2>
<ul>
<li>Manage Tokens Operations like regestering and refreshing</li>
<li>Format boilerplate api requests.</li>
<li>Provide simple functions to perform common api operations</li>
</ul>
<div>
There are two ways to manage your tokens.
<ol>
<li><b>Local File: </b>Read and Write to files on your computer. (refreshes tokens as needed)</li>
<li><b>Database: </b>Read from a database. (refresheds all tokens on a schedule)</li>
</ol>
The main difference between the two token managers is that the Database system supports multiple processes (or machines)<br>
where as the Local File system does not.<br>
If you do not need to have multiple processes the Local Manager is recommended since it is simpler to setup
</div>
</div>
<h2>Install Guide</h2>
<div>
Note: lines with $ mean execute this command in bash<br>
Example <code>$ ls</code> means enter ls into terminal
<ol>
<li>Clone the Repository<br>
<code>$ git clone https://github.com/ecobee/python_api_sdk.git</code></li>
<li>Navigate inside the root directory<br>
<code>$ cd python_api_sdk</code></li>
<li>Install the Repository<br>
<code>$ pip install .</code></li>
<li>Run the interactive enviornment setup<br>
<code>$ python setup_scripts/env_setup.py</code></li>
</ol>
</div>
<h2>User Guide</h2>
<div>
Note: Lines with >>> mean execute this command in python
<h3>Adding Users</h3>
<ul>
import the ApiInterface object<br>
<code>>>> from ebapi.api_interface import ApiInterface</code><br>
</ul>
<ul>
   create an ApiInterface<br>
<code>>>> interface = ApiInterface()</code>
</ul>
<ul>
Add a user<br>
<code>>>> interface.add_user()</code><br>
This will display a ecobee pin and pause execution<br> 
Navigate to www.ecobee.com and login with you username and password<br> 
Home (Top right) --> My Apps (Bottom Left) --> Add application (Enter into Text Field)<br>
Hit enter into you python session<br>

This will generate access and refresh tokens

</ul>
</div>
</body>
</html>
