from flask import Flask, request, redirect, render_template, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm, TaskForm, LoginForm
from passlib.hash import sha256_crypt  # for encrypting the password.
import datetime
import enum
# importing the dataset to plot on the graph
from graph import  dash, show_graph, dcc, html,dbc

import subprocess as sp
import pandas as pd
import json
import time

from apis.sched import schedule_tasks


# the path for the csv should be ./data/{{ task_name }}_{{ task_id }}.csv
# the path for the bots should be ./bots/{{ bot_name }}
# the route for the visuals will be /visuals/{{ task_id }}/{{ task_name }}



_bot_path ="./bots/"  # root folder for all the bots
_data_path = "./data/"  # root directory for the data files
_visuals_path = "" # root path for all the visuals


'''

StartProcessCron: "0 1/1 * 1/1 * ? *"
StartProcessCronDetails: "{"type":0,"minutely":{"atMinute":10},"hourly":{},"daily":{},"weekly":{"weekdays":[]},"monthly":{"weekdays":[]},"advancedCronExpression":""}
InputArguments: "{"task_id":3,"faculty_mail_id":"raghav.81-cse-17@mietjammu.in"}"
'''


# status ( status of the task )
class Status(enum.Enum):
    PE = 'PENDING', 'danger'  # status,css btn class
    AC = 'ACTIVE', 'info'
    CO = 'COMPLETED', 'success'


# creating the app
app = Flask(__name__)


# mysql uri

app.secret_key = "secret1234"
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://root:@localhost/rps_new'



# dash app with the baseurl as visuals and the bootstrap linked

dashapp = dash.Dash(__name__, server=app, url_base_pathname="/visuals/",external_stylesheets=[dbc.themes.BOOTSTRAP])

# changing the title

dashapp.title="Visuals"

# basic layout of the dashapp
dashapp.layout = html.Div([

    dcc.Location(id='url'),

    # html.Div(id='page-content'),
    
    html.Div(id='page-content',children=[
        
    
     html.Div(
    [   
        
      # the loading spinners
        html.Div(
        
        [
        dbc.Spinner(color="primary", type="grow"),
        dbc.Spinner(color="secondary", type="grow"),
        dbc.Spinner(color="success", type="grow"),
        dbc.Spinner(color="warning", type="grow"),
        dbc.Spinner(color="danger", type="grow"),
        dbc.Spinner(color="info", type="grow"),
        # dbc.Spinner(color="light", type="grow"),
        dbc.Spinner(color="dark", type="grow"),
        # dbc.Spinner(spinner_style={"width": "3rem", "height": "3rem"}),
        ],
        className="my-5"
        )],className="d-flex justify-content-center"
)
  
        
    ])
   
])

# inside the div tag with id=page-content with we are adding the component returned by the show_graph defined in the graphs.py file


@dashapp.callback(dash.dependencies.Output('page-content', 'children'),
                   [dash.dependencies.Input('url', 'pathname'),
                   ])
def show(pathname):
    print(pathname)
    if len(pathname)==0 or pathname=="/visuals/" or len(pathname)<30 and "%20" not in pathname:
        return dcc.Location(id="home",href="/404")
   

    time.sleep(2)
    return show_graph(pathname)


# db config
db = SQLAlchemy(app)





# task model
class Tasks(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.String(30), nullable=False,
                           default=datetime.datetime.now)
    created_by = db.Column(db.String(30), db.ForeignKey(
        'users.username'), nullable=False)  # one to many relation with the username
    start_date = db.Column(
        db.DateTime, default=datetime.datetime.now().date, nullable=False)
    end_date = db.Column(
        db.DateTime, default=datetime.datetime.now().date, nullable=False)
    sheet_name = db.Column(db.String(250),nullable=False)
    sheet_url = db.Column(db.String(1000), nullable=False)
    status = db.Column(db.Enum(Status), default=Status.PE)
    bot_assigned = db.Column(db.String(40), nullable=False)


# user model

class Users(db.Model):
    __table_args__ = {'extend_existing': True}
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(20), primary_key=True)
    email = db.Column(db.String(90), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    registered_at = db.Column(
        db.String(30), nullable=False, default=datetime.datetime.now)
    # and i have on delete cascade if the user is deleted all his tasks will be deleted.
    tasks = db.relationship('Tasks', backref='users', cascade="all,delete")


# route for register page
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    try:
        # fetching the firstmatch from db
        user = Users.query.first()
    except Exception as e:
            
        return render_template("maintenance.html")
    
    
    if request.method == 'POST' and form.validate():

        # create the user.
        user = Users(
            name=form.name.data,
            email=form.email.data,
            username=form.username.data,
            password=sha256_crypt.encrypt(str(form.password.data)),
        )
        
        
        try:
            # add to the db
            db.session.add(user)
            db.session.commit()

            # notify the user ur account has been created.
            flash("Your account has been created successfully", "success")

            return redirect(url_for("home"))
        except Exception as e:
            flash("Email or Username is already taken", "warning")
    return render_template("register.html", form=form)


# route for login page
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if request.method == 'POST':

        # fecthing the details from the form.

        username = form.username.data
        password_candidate = form.password.data
        try:
        # fetching the firstmatch from db
            user = Users.query.filter_by(username=username).all()
        except Exception as e:
            
            return render_template("maintenance.html")
        if len(user) > 0:
            # app.logger.info('NO such user')
            # flash("Make sure to register before login", "info")
            # return redirect(url_for("home "))

            # authenticating the user

            if username == user[0].username and sha256_crypt.verify(password_candidate, user[0].password):

                flash("You have successfully logged in", "success")

                # create the session variables
                session['logged_in'] = True
                session['username'] = username
                session['name'] = user[0].name
                session['email_address'] = user[0].email

                return redirect(url_for("dashboard", page=1))
            else:
                # flash("Incorrect Password","danger")
                error = "Invalid Login Credentials"
                return render_template("login.html", form=form, error=error)
        else:
            error = "User Not Found"
            return render_template("login.html",  form=form, error=error)
    return render_template("login.html",  form=form)


# route for s
@app.route("/logout")
def logout():
    if 'username' not in session:
        form=LoginForm(request.form)
        flash("No User Logged in", "warning")
        return render_template("login.html",form=form)
    form = LoginForm(request.form)
    session.clear()
    flash("You are now logged out", "success")
    return redirect(url_for("login"))


# route for task page.
@app.route('/task', methods=['GET', 'POST'])
def task():
    page = request.args.get("page")
    
    if 'username' not in session:
        flash("No User Logged in", "warning")
        return render_template("login.html")
    form = TaskForm(request.form)
    if request.method == 'POST' and form.validate() and form.validate_end_date(form.end_date) and form.validate_sheet_url(form.sheet_url):
        # function created by me to validate the enddate (enddate > startdate)

        new_task = Tasks(
            name=form.name.data,
            description=form.description.data,

            start_date=form.start_date.data,
            end_date=form.end_date.data,
            sheet_name=form.sheet_name.data,
            sheet_url=form.sheet_url.data,
            created_by=session["username"],
            status=Status.PE,
            bot_assigned=form.bot_assigned.data
        )

        db.session.add(new_task)
        db.session.commit()
        
        
        
        # schedule the bot here
        
       
        bot_name = str(new_task.bot_assigned.split(" ")[0])
        trigger_name = new_task.sheet_name +"_"  + str(new_task.id)
        stop_date = new_task.end_date.strftime("%Y-%m-%d")  
        
        print(bot_name)
        
        
        # parameters to be passed to the bot while scheduling
        
        
        start_date = new_task.start_date.strftime("%Y-%m-%d") 
        sheet_uri = new_task.sheet_url
        faculty_mail_id = session['email_address']
        task_id = new_task.id
        sheet = new_task.sheet_name
        curr_hour = datetime.datetime.now().today().hour 
        
        input_args = {
            
            "start_date": start_date,
            "end_date": stop_date,
            "sheet_url": sheet_uri,
            "task_id": task_id,
            "sheet": sheet,
            "faculty_mail_id": faculty_mail_id
            
            
            
        }
    
         # '''InputArguments: "{"start_date":"2020-11-18T15:10:00Z","sheet_url":"\"https://docs.google.com/spreadsheets/d/1kAI4siNQ-0ApPxwydfdeNpdWkrUKElS9R25T87dN_u0/edit#gid=747949193\"","end_date":"2020-11-19T15:10:00Z","faculty_mail_id":"raghav.81-cse-17@mietjammu.in","task_id":6,"sheet":"ACF"}'''
              
        if  "excel"  in str(new_task.bot_assigned).lower(): 
            
            long_running = True
            
        if "document" in str(new_task.bot_assigned).lower() or "synopsis" in  str(new_task.bot_assigned).lower():
            
            long_running = False
            
        
        schedule_tasks(bot_name =bot_name,trigger_name = trigger_name,input_arguments= input_args,curr_hour = curr_hour ,stop_date = stop_date,long_running =long_running)
        

        return redirect(url_for("dashboard", page=page))
    return render_template("task.html", form=form)


# dashboard
@app.route("/dashboard/<int:page>",methods=["GET","POST"])
def dashboard(page=1):
    per_page = 6
    if 'username' in session:
        # fetching the data from the tasks table only for the current user in the session and passing it to the view
        try:
            all_tasks = Tasks.query.filter_by(created_by=session["username"]).paginate(
                page, per_page, error_out=False)
        except Exception as e:
          
            return render_template("maintenance.html")
        
        ################## NOW BY SCHEDULE ALL DONE ####
        
        
        # pending_tasks = Tasks.query.filter_by(
        #     created_by=session["username"], status='PE').all()
        
        
        ## sort on basis of the start date 
        # pending_tasks = sorted(pending_tasks,key=lambda task : datetime.datetime.strptime(task.start_date.strftime("%Y-%m-%d"), "%Y-%m-%d"))
        
       

        # fetching all the pending tasks and then executing the bot to update the first PENDING TASK based on the task_id in the DB.
        # if len(pending_tasks) > 0:
        #     if "document" not in pending_tasks[0].bot_assigned: 
            
        #         print(pending_tasks[0].start_date.strftime("%Y-%m-%d"))
                
                ### TRY TO RUN THIS COMMAND INITIALLY FROM PYTHON TO  INVOKE BOT ##
                
                # cmd = 'uirobot execute --file "D:\\ACF\\db_connect.xaml" --input "{\'id\':\'' + str(
                #     pending_tasks[0].id) + "'}\""  # COMMAND TO EXECUTE BOT USING UIROBOT
                # print(cmd)

                #################################################################
                # 
                # if  "excel"  in str(pending_tasks[0].bot_assigned).lower(): 
                    # cmd = 'uirobot execute --file "D:\\c_data\\future\\MYPROJECTS\\RPA\\RPA-20201111T195024Z-001\\RPA\\MonitorExcelBot.xaml" --input "{\'sheet\':\''+ str(pending_tasks[0].sheet_name)+ '\' ,\'start_date\':\''+ str(pending_tasks[0].start_date) +'\',\'end_date\':\''+ str(pending_tasks[0].end_date)+'\',\'sheet_url\': \''+str(pending_tasks[0].sheet_url)+'\',\'task_id\':'  + str(
                    #     pending_tasks[0].id) +' }"'
                    
                    
                     # schedulig parameters
                    # bot_name = pending_tasks[0].name
                    # trigger_name = pending_tasks[0].sheet_name +"_"  + str(pending_tasks[0].id)
                    # stop_date = pending_tasks[0].end_date.strftime("%Y-%m-%d")
                    # long_running = True
                    
                    
                    # print(stop_date)
                    
                    
                
                # elif "document" in str(pending_tasks[0].bot_assigned).lower():
                    # cmd = 'uirobot execute --file "D:\\c_data\\future\\MYPROJECTS\\RPA\\sahil_and_all_basics-20201113T085914Z-001\\sahil_and_all_basics\\pdf_sahil.xaml" --input "{\'sheet\':\''+ str(pending_tasks[0].sheet_name)+ '\',\'start_date\':\''+ str(pending_tasks[0].start_date) +'\',\'end_date\':\''+ str(pending_tasks[0].end_date)+'\',\'sheet_url\': \''+str(pending_tasks[0].sheet_url)+'\',\'task_id\':'  + str(
                    #     pending_tasks[0].id) +' }"'
                    
                    # schedulig parameters
                    # bot_name = pending_tasks[0].name
                    # trigger_name = pending_tasks[0].sheet_name +"_"  + str(pending_tasks[0].id)
                    # stop_date = pending_tasks[0].end_date.strftime("%Y-%m-%d")
                    # long_running = False
                
                #### DEBUG ##########
                
                # print(cmd)
                
                ##########
                
                # subprocess module is used to execute the  system command
                # print(sp.getoutput(cmd))
                
                
                
                # schedule_tasks("HelloBol",trigger_name,stop_date,long_running)
                
                
            
            
            #################  PREVIOUS COMMAND ###############################
            
            # sp.getoutput('uirobot execute --file "D:\\c_data\\future\\MYPROJECTS\\RPA\\RPA-20201111T195024Z-001\\RPA\\rpadatetest.xaml" --input "{\'sheet\': \'ACF\' ,\'start_date\': \'2020-10-05 00:00:00\',\'end_date\': \'2020-10-07 00:00:00\',\'sheet_url\': \'https://docs.google.com/spreadsheets/d/1VE4mn4MwnCt2L_ShOhQ7nwth2HNB4kOOJNZoyoEMPTs/edit#gid=1830777927\',\'task_id\':'  + str(
            #     pending_tasks[0].id) +' }"')
            
            ####################################################################

        return render_template("dashboard.html", tasks=all_tasks,start_date =str(datetime.datetime.now()) ,current_user=str(session['name']).title())
    flash("No User Logged in", "warning")
    form = LoginForm(request.form)
    return render_template("login.html",form=form)

# handling 404 error


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


@app.route("/about")
def about():
    return render_template("about.html")

#####################################################################################################################################################

################## CHART.JS #################
# graph new

@app.route('/graph/<int:task_id>/<string:task_name>')
def graph(task_id,task_name,chartID = 'chart_ID', chart_type = 'pie', chart_height = 500):
    if 'username' in session:

        task=Tasks.query.get(task_id)
        
        
        sheet_name=str(task.sheet_name)
        
        
        data_path=f"{_data_path}{sheet_name}_{task_id}.csv"
        print(data_path)
        
        
        df=pd.read_csv(data_path)
        
        student_count=len(df)-5
        name_count = []
        for m in range(1, student_count+1):
            s = [i for i in df.iloc[m]]
            name = s[2]
            count_undone = 0
            for i in s[3:-2]:

                if i == 'N':
                    count_undone += 1

            name_count.append([name, count_undone])
            
        df=pd.DataFrame({"name":[i[0] for i in name_count],"incomplete":[i[1] for i in name_count]})

        # dashapp.layout = show_graph()
        # return dashapp._layout
        chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}
        data = {'datasets': [{'data': df["incomplete"].values.tolist()}], 'labels': df["name"].values.tolist()}
        print(df["name"].values.tolist())
        return render_template('graph.html', chartID=chartID,  data=df["incomplete"].values.tolist(),labels=df["name"].values.tolist(),task=task)
    flash("No User Logged in", "warning")
    return redirect(url_for("login"))

######################################################################################################################################################


# home page
@app.route('/')
def home():
    return render_template("index.html")


if __name__ == '__main__':

    app.run(debug=True)
    # dashapp.run_server(port=9000)
