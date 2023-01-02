❖	To deploy our system a user needs to follow the following  steps:
1.	First of all a user needs to install python and django. Python can be downloaded from here and Django can be downloaded from here.
2.	Then he needs to install the Oracle Database. Instructions to install the database can be found here.
3.	Then the user needs to open the project folder in a python supported IDE.
4.	Now to connect the system with the database the user needs to install the mysqlclient sequalizer from the terminal. To install that the command is 
●	pip install mysqlclient
5.	Now user needs to create the database and to create the tables user have to give the following commands:
●	python manage.py makemigrations
●	python manage.py migrate
6.	Now before running the localhost the user must needs to install some modules. To install the modules the commands are given below:
●	pip install twilio
●	pip install xhtml2pdf
7.	Finally to run the localhost server user needs to give the following command:
●	python manage.py runserver

