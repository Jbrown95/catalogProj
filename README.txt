1. Git clone this repository.
2. cd into the location in which you cloned this repository.
3. (if virtualenv is installed skip this step) 'pip install virtualenv'.
4. run 'virtualenv ./venv'
5. run 'venv/bin/activate'.
6. run 'pip install -r requirements.txt'
7. run application by running 'sudo python application.py'



1. The IP address: 18.214.39.83, SSH port 2200.
2. URL: http://18.214.39.83:80
3. Python,pip,virtaulenv and all the required packages were installed manually ("apt-get install python/python-pip/virtualenv" and  "pip install -r requirements.txt"). 
4. The set up is very simple. I am using SQLAlchemy, a python package. whcih is using the native python DB, SQLite. It handles the entire DB beautifully and requires no setup as far as this user is concerned. Pre-configured if you will. I also added a "forever" script to hopefully prevent crashes from keeping the app down. 
5. A list of any third-party resources you made use of to complete this: The big gun...stackoverflow. For some stuff about configuring sshd, keygen etc. And AWS docs. 
6. I installed Python2.7, pip, and some packages located in requirements.txt. Ran the normal (apt update/upgrade). Disabled the normal ssh port. opened ports described in the project details. Changed the time to UTC. The grader should have a login, with ssh access using the provided .pem. 

Configuring Server:
1. Go to https://lightsail.aws.amazon.com/ls/webapp/home/instances and start an ubuntu instance.
2. Log into the instance using SSH. (I used my own ssh, and the .pem provided by AWS)
3. 'ssh -i PEM.pem ubuntu@ip.ip.ip.ip'
4. 'sudo apt update'
5. 'sudo apt upgrade'
6. 'sudo apt-get install python'
7. 'sudo apt-get install python-pip'
8. 'sudo adduser grader'
   Enter new UNIX password: password
   Retype new UNIX password: password
9. add "USERNAME ALL=(ALL) ALL" to /etc/sudoers
10. 'mkdir .ssh' in /home/grader
11. 'cd .ssh'
12. 'ssh-keygen'
13. 'cp id_rsa.pub authorized_keys'
14. 'mv id_rsa id_rsa.pem'(Becomes the file input for ssh as grader)
Configure Firewall/ports
1. 'sudo vi /etc/ssh/sshd_config'
2. change the "Port 22" line to read "Port 2200"
3. 'sudo ufw allow <port number>' (repeat for ports 123,80,2200)
4. 'sudo ufw deny 22'
The AWS firewall must be changed on the instance inside the AWS lighstail web-console. 
1. navigate to your own instance
2. open the networking tab
3. remove port 22 and add ports 2200,123




