# RPA FACULTY ASSISTANT

> It is a web application made in flask framework and is integrated with the RPA(Robottic Porcess Automation) using the UiPATH Orchestrator Api and Gsheet Api.
> It has two bots one for monitoring the updates in the excel sheet and other one is to check for some document like ppt and synposis presence in some drive.
> The sheets should be in the specific format , the format is provided in the below links:

- [EXCEL DOCUMENT](WebApp/static/files/template_monitor.xlsx)
- [DOCUMENT DETECTION](WebApp/static/files/template_document.xlsx)
https://github.com/MIETDevelopers/2017_CSEA2_P7_RPA_FacultyAssistant_Raghav_Umang_Vastavik_Samar_Sahil/tree/master/WebApp/templates/admin
> It has the admin page and the user page and visuals using dash app for the user.
> Admin can create users and the users can assign the Task.
> SQLALCHEMY ORM is used.

#### Team Members

        - Raghav Gupta
        - Umang Bhan
        - Vastvik  Upadhaya
        - Samar Kant Bhasin
        - Sahil Singh

- [MAIN APP FILE](WebApp/app.py)

- [FORM CLASS FILES](WebApp/forms.py)

- [GRAPH PROGRAM](WebApp/graph.py)

- [SCHEDULING PROGRAM](WebApp/apis/sched.py)

- [GSHEET VALIDATION PROGRAM](WebApp/apis/gsheet.py)

- [TEMPLATES](WebApp/templates/)

  - [HOMEPAGE](WebApp/templates/index.html)

  - [LOGIN PAGE](WebApp/templates/login.html)

  - [ADMIN LOGIN PAGE](WebApp/templates/admin/index.html)

  - [ASSIGN TASK PAGE](WebApp/templates/task.html)

  - [DASHBOARD PAGE](WebApp/templates/dashboard.html)

  - [CUSTOM 404 PAGE](WebApp/templates/404.html)

- [STATIC FILES](WebApp/static/)

- **DATABASE**: [mysql](WebApp/db)

            - tasks table
            - users table

### CONFIGURATION FILE (WebApp/config.json):

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
