import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc   # bootstrap components  for dash app
import json

with open("config.json") as fp:
    params = json.load(fp)["params"]
# data directory
_data_path = params["DATA_ROOT_DIR"]

def show_graph(pathname):

    
    # print("PATNAME: ", pathname.split("/"))
    
    task_id=pathname.split("/")[2]
    
    task_name=pathname.split("/")[3].split("%20")[0]
    
    
    actual_data_path=_data_path+task_name+"_"+task_id+".csv"
    
    
    # print(actual_data_path)
    # path of the csv retireved by the bot.
    df = pd.read_csv(
        actual_data_path)
    
    
    # getting the row number of Total completed students
    complete_loc = 0


    for row_name in df["Name"]:
        
        if type(row_name) != str:
            complete_loc+=1
                
        elif "Completed" in row_name:
            break
        else:
            complete_loc+=1
                
                
    # print(df.iloc[complete_loc,:])

    # getting the row number of total pending 
    pending_loc = 0


    for row_name in df["Name"]:

        if type(row_name) != str:
            pending_loc+=1
                
        elif "Pending" in row_name:
            break
        else:
            pending_loc+=1
                
    # print(df.iloc[pending_loc,:])

        
    # print(df.loc[-1:])

    # student number who has completed the modules
    sc = df.iloc[complete_loc,:]

    # print(sc)
    # student number who has not completed the modules
    st = df.iloc[pending_loc,:]

    # print(st)
    # module names
    modules = df.columns[3:-2]

    
    # print(modules)
    # total students excluding the headers from top and bottom 3 fields
    student_count = len(df)-5

    # count of students who has done.
    students_done = [(float(i)) for i in sc.values[3:-2]]

    # count of students who has not done the task.
    students_undone = [(float(i)) for i in st.values[3:-2]]

    # count of incomplete modules with the student name
    # format:[[student_name,count]]
    name_col_index=df.columns.get_loc('Name')
    
    name_count = []
    for m in range(1, student_count+1):
        s = [i for i in df.iloc[m]]
        name = s[name_col_index]
        count_undone = 0
        for i in s[3:-2]:

            if i == 'N':
                count_undone += 1

        name_count.append([name, count_undone])

    df = pd.DataFrame({"name": [i[0] for i in name_count],
                       "incomplete": [i[1] for i in name_count]})
    
    # print(df)

    # if length of df is greater than one then show this.
    if len(df) > 1:
        fig = px.pie(df, values='incomplete', names="name",
                     title='Modules Incomplete Per Student', hole=0.3)
    else:
        fig = px.pie(df)

    fig.update_traces(textposition='inside', textinfo=None)
    # fig.update_layout( uniformtext_mode='hide')

    return html.Div([

        # spliting the url to get the title.

        html.H1('{}'.format("".join(pathname.split("/")
                                    [4].replace("%20", "   ").title())), className="text-center"),

        dcc.Graph(
            id='SampleChart',

            figure={

                'data': [{"x": modules, 'y': students_done, 'type': 'bar', 'name': 'Completed'},

                         {"x": modules, 'y': students_undone,
                          'type': 'bar', 'name': 'Incomplete'}
                         ],

                'layout': go.Layout(

                    xaxis={'title': 'Modules'},
                    yaxis={'title': 'Number of students '}
                 ),

            }

        ),

        html.Br(),
        
         html.Center(

            children=[


                 dcc.Graph(
                    id='SampleChar3',
                    className="my-2",
                    figure=fig


                    )
                 ]
            ),

        ], className="jumbotron"
    )

