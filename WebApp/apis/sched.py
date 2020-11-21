import requests
import json
import datetime 

### CREDENTIALS:


tenant_name = "TENANT_NAME"

account_logical_name="ACCOUNT LOGICAL NAME"


refresh_token = "USER KEY"
 
client_id  =  "CLIENT ID"




def schedule_tasks(bot_name,trigger_name,input_arguments,curr_hour,stop_date,long_running):
    
    access_token = auth()
    
    release_info = process_info(access_token)
    
    print(release_info)
    release_id = ""
    release_name = ""
    for bot in release_info:
        if bot_name.lower() in bot["name"].lower():
            release_id = bot["id"]
            release_name =bot["name"]
            
    
    print(release_id,release_name)
    
    # now to schedule.
    
    process_headers = {    
            
                "Authorization": "Bearer "+str(access_token),
                "X-UIPATH-TenantName": tenant_name,
                "Content-Type": "application/json",
                "X-UIPATH-OrganizationUnitId": "633869" # folder id
            
            }
    
    
    # endpoint for scheduling
    
    schedule_url = f"https://cloud.uipath.com/{account_logical_name}/{tenant_name}/odata/ProcessSchedules"

    # start cron exp and desc
    start_cron_exp = "0 0/1 * 1/1 * ? *"
    start_cron_desc = "{\"type\":0,\"minutely\":{\"atMinute\":1},\"hourly\":{},\"daily\":{},\"weekly\":{\"weekdays\":[]},\"monthly\":{\"weekdays\":[]},\"advancedCronExpression\":\"\"}"
    
    
    t_hour = str(datetime.datetime.now().time().hour)
    
    t_hour = "00" if t_hour == "24" else  t_hour
    
    
    if len(str(t_hour))<2:
        t_hour="0"+t_hour
        
        
    t_min = str(datetime.datetime.now().time().minute+1)
    
    
    if len(str(t_min))<2:
        t_min = "0"+t_min    
        
        
    to_add = "T"+t_hour+":"+t_min+":00Z"
    
    
    # stop date expression.
    stop_date = stop_date  # stop date shoudl be in the string format lie %Y-%M-%D
    

    
    curr_hour = 00 if curr_hour+2 >= 24 else curr_hour+2
        
    
    s_min = str(datetime.datetime.now().minute)
    s_hr = str(datetime.datetime.now().hour)
    
    s_hr = "00" if s_hr == "24" else s_hr
    
    print(stop_date)
    # long running would be a bool , representing that the job type is long or not.
    if long_running:
        start_cron_exp = f"0 {s_min} {curr_hour} 1/1 * ? *"
        start_cron_desc = "{\"type\":2,\"minutely\":{},\"hourly\":{},\"daily\":{\"atHour\":\""+str(curr_hour)+"\",\"atMinute\":"+str(s_min)+"},\"weekly\":{\"weekdays\":[]},\"monthly\":{\"weekdays\":[]},\"advancedCronExpression\":\"\"}"
        stop_date = stop_date + "T23:59:00Z"
    else:
        stop_date+=to_add


    if(len(s_min)<2):
        s_min  = "0"+s_min

    if(len(s_hr)<2):
        s_hr  = "0"+s_hr

    s_to_add = "T"+ s_hr+":"+s_min+":"+"00Z"
    
    input_arguments["start_date"] = input_arguments["start_date"]+ s_to_add
    
    input_arguments["end_date"] = stop_date
    
    input_arguments = json.dumps(input_arguments)
    
    
    print(input_arguments)
    
    # request body data needed to be passed to the orcherastator.
    schedule_data = {
        
        
        "Name": trigger_name,
        "ReleaseId": release_id,
        "ReleaseName": release_name,
        "StartProcessCron": start_cron_exp,
        "StartProcessCronDetails": start_cron_desc,
        "StartStrategy": -1,
        "ExecutorRobots": [],
        "StopProcessExpression": "",
        "StopStrategy": "Kill",
        "StopProcessDate": stop_date,
        "TimeZoneId": "India Standard Time",
        "InputArguments": input_arguments
    }

    print(schedule_data)

    # post request.
    schedule_response = requests.post(url=schedule_url,data=json.dumps(schedule_data),headers=process_headers)
    
    
    print(schedule_response.text,schedule_response.status_code)

    if schedule_response.status_code not in [200 ,201]:
        return False
    return True





def auth():
    
    url="https://account.uipath.com/oauth/token"

    data={
        
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id
    }
    headers={
        
        "Content-Type": "application/json",
        "X-UIPATH-TenantName": tenant_name
    }
    response = requests.post(url,data=json.dumps(data),headers=headers)


    access_token = json.loads(response.text)["access_token"]
    
    
    return access_token







    # retieving the process release key
def process_info(access_token):
   
    

    # process_url = f"https://cloud.uipath.com/{account_logical_name}/{tenant_name}/odata/Releases?$filter= Name eq 'HelloBol_DevEnv'"  # correct url 

    process_url =  f"https://cloud.uipath.com/{account_logical_name}/{tenant_name}/odata/Releases"
    
    
    process_headers = {    
            
                "Authorization": "Bearer "+str(access_token),
                "X-UIPATH-TenantName": "MIETDefault",
                "Content-Type": "application/json",
                "X-UIPATH-OrganizationUnitId": "633869"
            
            }


    process_response = requests.get(url=process_url,headers=process_headers)
    process_releases = json.loads(process_response.text)
    release_info = []
    
    organization_unit_id = json.loads(process_response.text)["value"][0]["OrganizationUnitId"]
    
   
   
    for release in process_releases["value"]:
        
        release_id = release["Id"]
        release_name = release["Name"]
        release_info.append({"name":release_name,"id":release_id})
    


    return release_info




# print(schedule_tasks("HelloBol","HelloWorldddddddsasadadss","2020-11-20",True))


#####################  GET BOT ID AND START JOB ##################


    # retreiving the robot id
    # robot_url = f"https://cloud.uipath.com/{account_logical_name}/{tenant_name}/odata/Robots"


    # robot_response =  requests.get(url=robot_url,headers=process_headers)

    # robot_id=json.loads(robot_response.text)["value"][0]["Id"]


    # print(robot_id)





    # starting the job

    # start_job_url = f"https://cloud.uipath.com/{account_logical_name}/{tenant_name}/odata/Jobs/UiPath.Server.Configuration.OData.StartJobs"

    # robots_ids=[robot_id]
    # print(str(release_key))
    # data={
        
        
    # "startInfo": {
    #     "ReleaseKey": str(release_key),
    #     "Strategy": "All",
    #     "RobotIds": robots_ids,
    #     "JobsCount": 0,
    #     "NoOfRobots": 0,

    
    # }
    
    # }

    # print(json.dumps(data))


    # start_job_response = requests.post(start_job_url,data=data,headers=process_headers)



    # print(start_job_response.text)


    # scheduling 




# schedule_stop_url = f"https://cloud.uipath.com/{account_logical_name}/{tenant_name}/odata/ProcessSchedules(51675)"

# params={
# "setEnabledParameters":{
    
#     "scheduleIds":[51675],
#     "value":"false"
    
# }
# }


# print(requests.delete(schedule_stop_url,headers=process_headers).text)

