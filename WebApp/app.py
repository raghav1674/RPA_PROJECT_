from flask import Flask, request, redirect, render_template, url_for, flash, session, jsonify
# from flask_sqlalchemy import SQLAlchemy
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
from models import db,Users,Tasks,Status
from apis.sched import schedule_tasks

# from crypto import encrypt,decrypt ## for encryption

# ADMIN PANEL
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink  # adding logout link inthe menu bar

# MAIL
from flask_mail import Mail




# the path for the csv should be ./data/{{ task_name }}_{{ task_id }}.csv
# the path for the bots should be ./bots/{{ bot_name }}
# the route for the visuals will be /visuals/{{ task_id }}/{{ task_name }}

# loading the configurations of our app from config.json

with open("config.json") as fp:
    params = json.load(fp)["params"]


_bot_path = params["BOT_ROOT_DIR"] # root folder for all the bots
_data_path = params["DATA_ROOT_DIR"]   # root directory for the data files
_visuals_path = "" # root path for all the visuals



# creating the app
app = Flask(__name__)





# mysql uri

app.secret_key = params["APP_SECRET_KEY"]

if params["LOCALHOST"]:
    app.config["SQLALCHEMY_DATABASE_URI"] = params["LOCALHOST_SQLALCHEMY_DATABASE_URI"]
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = params["PROD_SQLALCHEMY_DATABASE_URI"]
    


# MAIL CONFIG

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params["ADMIN_EMAIL"],
    MAIL_PASSWORD=params["ADMIN_PASSWORD"],
    MAIL_ASCII_ATTACHMENTS=True
)

# MAIL

mail = Mail(app)


# db config
# db = SQLAlchemy(app)

db.init_app(app)



# ADMIN PANEL

admin = Admin(app,template_mode='bootstrap3')
class UserView(ModelView):
    #     # column_display_pk = True
#     # column_edit_pk = True
#     # list_columns=['name','username','email','password','registered_at']
    column_searchable_list = [ 'email','name']
    

    form_excluded_columns = ['tasks', 'registered_at']
    
    def is_accessible(self):
        if "admin_login" in session:
           return True
        return False 
    
    def on_model_change(self, form, model, is_created):
        # send the email to the user created.
        email_id = form.email.data        
        user_pass = form.password.data         
        user_username = form.username.data 
        mail.send_message("RPA FACULTY ASSISTANT ACCOUNT CREATED!",
                          sender=params["ADMIN_EMAIL"],
                          recipients=[email_id],
                          body="Your account has been created.\n\nUsername: %s\nPassword: %s"%(user_username,user_pass)
        )
        super().on_model_change(form, model, is_created)       

admin.add_views(UserView(Users,db.session))
admin.add_link(MenuLink(name='Log out', url='/admin/logout'))
# admin.add_views(ModelView(Tasks,db.session))


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





# route for login page
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if request.method == 'POST':

        # fecthing the details from the form.

        username = form.username.data
        password= form.password.data
        try:
        # fetching the firstmatch from db
            user = Users.query.filter_by(username=username).all()
        except Exception as e:
            
            return render_template("maintenance.html")
        if len(user) > 0:
            # app.logger.info('NO such user')
            # flash("Make sure to register before login", "info")
           

            # authenticating the user

            if username == user[0].username and user[0].password ==password:

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
    if request.method == 'POST' and form.validate() and form.validate_end_date(form.end_date) and form.validate_sheet_url(form.sheet_url)  and form.validate_sheet_name(form.sheet_url):
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
    
       
              
        if  "excel"  in str(new_task.bot_assigned).lower(): 
            
            long_running = True
            
        if "document" in str(new_task.bot_assigned).lower() or "synopsis" in  str(new_task.bot_assigned).lower():
            
            long_running = False
            
        
        schedule_tasks(bot_name =bot_name,trigger_name = trigger_name,input_arguments= input_args,curr_hour = curr_hour ,stop_date = stop_date,long_running =long_running)
        print("executed commad ",long_running)
        

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
        
       

        return render_template("dashboard.html", tasks=all_tasks,start_date =str(datetime.datetime.now()) ,current_user=str(session['name']).title())
    flash("No User Logged in", "warning")
    form = LoginForm(request.form)
    return render_template("login.html",form=form)




# admin login

@app.route("/admin/",methods=['GET','POST'])
def admin_login():
    
    # print(session.get("admin_login"),session.get("admin_login",False) is True)
    
    if session.get("admin_login",False) is True:
       
        return redirect("/admin/users/")
    
    elif request.method == 'POST':
        admin_email = request.form["admin_email"]
        admin_password = request.form["admin_pass"]
        if admin_email == params["ADMIN_EMAIL"] and admin_password == params["ADMIN_PASSWORD"]:
            flash("You have successfully logged in", "success")
            session["admin_login"] = True 
            return redirect("/admin/users")
        else:
            flash("Invalid Credentials","danger")
            return render_template("/admin/index.html")
    flash("You are not authorized","warning")
    return render_template("index.html")
   
   
    
# admin logout
@app.route("/admin/logout")
def admin_logout():
    if 'admin_login' in session:
        del session["admin_login"]
        flash("You are now logged out", "success")
        return redirect("/admin/")
    flash("You are not Authorized","danger")
    return redirect(url_for("home")) 
 
 
    
# handling 404 error

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


@app.route("/about")
def about():
    return render_template("about.html")



################## CHART.JS #################
# graph new

@app.route('/graph/<int:task_id>/<string:task_name>')
def graph(task_id,task_name,chartID = 'chart_ID', chart_type = 'pie', chart_height = 500):
    if 'username' in session:

        task=Tasks.query.get(task_id)
        
        
        sheet_name=str(task.sheet_name)
        
        
        data_path=f"{_data_path}{sheet_name}_{task_id}.csv"
   
        
        
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

  
        chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}
        data = {'datasets': [{'data': df["incomplete"].values.tolist()}], 'labels': df["name"].values.tolist()}
        print(df["name"].values.tolist())
        return render_template('graph.html', chartID=chartID,  data=df["incomplete"].values.tolist(),labels=df["name"].values.tolist(),task=task)
    flash("No User Logged in", "warning")
    return redirect(url_for("login"))



# home page
@app.route('/')
def home():
    return render_template("index.html")


# Not Authenticated route
@app.errorhandler(403)
def page_not_found(e):
    # note that we set the 404 status explicitly
    flash("You are not Authorized","danger")
    return render_template('index.html'), 403


if __name__ == '__main__':

    app.run(debug=True)

