# Outline Distribution
The repository provides a full Django implementation to run a simple [Outline VPN](https://getoutline.org/) distribution system. The provided server code gives you what you need to handle Outline server inventory, and API system required for running Telegram Bot, Email Bot and other interfaces.

## Installation
You will need a Django server in order to use this repository. Run the following instructions to get your system up and running. The instruction is based on Python 3.8. You have to make required changes if you are using a different version of the python.

### Project directory
Create a directory to hold your project files, and change into that directory.

### Virtualenv
Install [virtualenv](https://virtualenv.pypa.io/en/stable/) on your system. Once installed create a virtualenv directory to isolate your packages.

Now run:
`virtualenv env -p python3.8`

This will create `env` directory using python 3.8 and copies all the base binaries, scripts and libraries into it.

Activate the virtualenv
`source ./env/bin/activate`

### Django
Install django using pip and create a project:
`pip install django`
`django-admin startproject out_dist`

### Clone git repo
Clone this repository
`https://github.com/ASL-19/outline-distribution.git`
`cd outline-distribution`

### Required python packages
Install required package by running
`pip install -r requirements.txt`

NOTE: It overwrites your django with the one this project is written for. If you need to change that you may need to modify some code

### Add apps to your django
Modify your settings and add the new apps to your project settings file `out_dist/settings.py`

Add `distribution`, `server` and `preference` to your INSTALLED_APPS list.
```
INSTALLED_APPS = [
    ...
    'distribution',
    'server',
    'preference'
]
```
Save the file and run the following command to update the database. If you are using the default django it should create a sqlite db file for you.
`python ./manage.py migrate`

### Create Admin
Create an super admin user for your django system by running:
`python ./manage.py createsuperuser`

Enter values for your user, email and password.

### Run the app
Now you should be able to run the app and browse the admin section
`python ./manage.py runserver`

By default it run your server on `http://127.0.0.1:8000/`

You should be able to see admin section on `http://127.0.0.1:8000/admin/`

Login with your super admin user.

### Use the app
Once in admin section you can add your Outline servers to your server app, and use the outline telegram bot to add users to your system.

## Plan
In case there is a need from community we are going to release these as PIP modules.
