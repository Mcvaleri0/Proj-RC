How to run this project:
python3 <filename> <attributes>

<attributes> are specific for every file and are explicit in the project document
For example:
central server: python3 centralServer.py -p CSport

user: python3 user.py -n CSname -p CSport

working server: python3 workingServer.py PTC(n) -p WSport -n CSname -e CSport

Note: <filename> needs to have a .py extension