# RPA FACULTY ASSISTANT

> It is a web application made in flask framework and is integrated with the RPA(Robottic Porcess Automation) using the UiPATH Orchestrator Api and Gsheet Api.
> It has two bots one for monitoring the updates in the excel sheet and other one is to check for some document like ppt and synposis presence in some drive.
> The sheets should be in the specific format , the format is provided in the below links:

- [EXCEL DOCUMENT](static/files/template_monitor.xlsx)
- [DOCUMENT DETECTION](static/files/template_document.xlsx)

> It has the admin page and the user page and visuals using dash app for the user.
> Admin can create users and the users can assign the Task.
> SQLALCHEMY ORM is used.

#### Team Members

        - Raghav Gupta
        - Umang Bhan
        - Vastvik  Upadhaya
        - Samar Kant Bhasin
        - Sahil Singh

- [MAIN APP FILE](app.py)

- [FORM CLASS FILES](forms.py)

- [GRAPH PROGRAM](graph.py)

- [SCHEDULING PROGRAM](apis/sched.py)

- [GSHEET VALIDATION PROGRAM](apis/gsheet.py)

- [TEMPLATES](templates/)

  - [HOMEPAGE](templates/index.html)

  - [LOGIN PAGE](templates/login.html)

  - [ADMIN LOGIN PAGE](templates/admin/index.html)

  - [ASSIGN TASK PAGE](templates/task.html)

  - [DASHBOARD PAGE](templates/dashboard.html)

  - [CUSTOM 404 PAGE](templates/404.html)

- [STATIC FILES](static/)

- **DATABASE**: [mysql](db)

            - tasks table
            - users table

### CONFIGURATION FILE (config.py):

'''json

      "LOCALHOST":true,

      "LOCALHOST_SQLALCHEMY_DATABASE_URI":"", // mysql server url for localhost

      "PROD_SQLALCHEMY_DATABASE_URI":"mysql production server url ",


      "DATA_ROOT_DIR":"./data/", // Data directory where all the excel files for processing and visuals will be created.


        "BOT_ROOT_DIR":"./bots/",  // Path of the Bots folder


        "APP_SECRET_KEY":"secret1234",  //Secret key to avoid csrf attack


        "ADMIN_EMAIL":" ",  // Admin email id


        "ADMIN_PASSWORD":" ", admin password


        "OAUTH_CREDENTIALS_FILE_PATH": "",   // oauth credntials used for gsheet activity should be in

                                                                                                        %APPDATA%\Roaming\\gspread\\credentials.json
                                                                                                    also used for gsuite activity in UIRobot

            Credentials used for scheduling

        "ORCHESTRATOR_TENANT_NAME": "", // orchestrator Tenant name

        "ORCHESTRATOR_ACCOUNT_LOGICAL_NAME": "", // orchestrator Acoount logical name

        "ORCHESTRATOR_ACCOUNT_USER_KEY": "",  // user key

        "ORCHESTRATOR_ACCOUNT_CLIENT_ID": "" client id

'''

### REQUIRED CREDENTIALS:

- **OAUTH CREDENTIALS**: required for gsuite activity.
- **MACHINE KEY , TENANT NAME, USER KEY AND CLIENT ID** : scheduling bots using Orchestrator

- UIPATH STUDIO should be installed on the system.

- Python 3.4 and above should be installed.
