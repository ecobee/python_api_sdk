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
Note: bolded lines with $ mean execute this command in bash<br>
Example <b>$ ls</b> means enter ls into terminal
<ol>
<li>Clone the Repository<br>
<b>$ git clone https://github.com/ecobee/python_api_sdk.git</b></li>
<li>Navigate inside the root directory<br>
<b>$ cd python_api_sdk</b></li>
<li>Install the Repository<br>
<b>$ pip install .</b></li>
<li>Run the interactive enviornment setup<br>
<b>$ python setup_scripts/env_setup.py</b></li>
</ol>
</div>
<h2>User Guide</h2>
<div>
Note: Bolded Lines with >>> mean execute this command in python
<h3>Adding Users</h3>
<ul>
import the ApiInterface object<br>
<b>>>> from ebapi.api_interface import ApiInterface</b><br>
</ul>
<ul>
create an ApiInterface
<b>>>> interface = ApiInterface()</b>
</ul>
<ul>
  Add a user <br>
  <b>>>> interface.add_user()</b>
  This will display a ecobee pin and pause execution
 
</ul>
</div>
</body>
</html>
