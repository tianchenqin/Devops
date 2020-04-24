"""
Author: Stefan Scheungrab <stefan.2.scheungrab@continental-corporation.com>
Lamdba for SMT Group creation:
    Parameters:
        account_type
        aws_account_id
        account_id
        division

"""
import requests
import boto3
import ssl
from datetime import datetime, timedelta

ssl._create_default_https_context = ssl._create_unverified_context

def find_key(key, dictonary):
    for k, v in dictonary.items():
        if k == key:
            return v
        elif isinstance(v, dict):
            result = find_key(key,v)
            if result:
                return result

def create_smt(event, context):
    smt_rest_uri = "https://rrm001.cw01.contiwan.com/SMTPublicRESTApi/Api/Group"
    
    proxy = {
        'http': "http://uidt589z:Windows2000@cias3basic.conti.de:8080",
        'https': "http://uidt589z:Windows2000@cias3basic.conti.de:8080"
    }
 
    account_type = find_key("account_type", event)
    aws_account_id = find_key("aws_account_id", event)
    account_owner = find_key("account_owner", event)
    account_id = find_key("account_id", event)
    division = find_key("division", event)

    dynamodb = boto3.resource("dynamodb")

    if ('task' in event):
        task = event['task']
        current_task = int(task['current_task'])
        divisional = find_key("divisional",event)
        division = divisional["division"]
    else:
        task = {}

    smt_groups = dynamodb.Table("conti_prov_smtgroups")

    smt_group = smt_groups.get_item(
        Key={'account_type': account_type}
        )['Item']
    
    cloudaccount_id = ""
    if account_type == "Amazon":
        cloudaccount_id = "{}-".format(str(aws_account_id))
    if account_type == "Alibaba":
        cloudaccount_id = "{}-".format(str(aws_account_id))
        account_id = ""
    extended_groups = ["ResourceAdmin", "ReadOnly", "BillingAdmin", "Auditor", "C_Resource-Admin", "C_ReadOnlyAccess", "C_Billing-Admin", "C_Auditor"]
    print(account_type)
    if account_type == "Azure":
        if 'created_at' in task['tasks'][str(current_task)]:
            time_now = datetime.now()
            created_time = datetime.strptime(task['tasks'][str(current_task)]['created_at'], "%Y-%m-%d %H:%M:%S.%f")
            timedelta = time_now - created_time
            if (timedelta.seconds / 60 ) >= int(30):
                time = "{}".format(datetime.now())
                task['tasks'][str(current_task)]['completed'] = True
                task['current_task'] = int(current_task + 1)
                task['tasks'][str(current_task)]['completed_at'] = time
                dynamodb.Table("jobs").put_item(Item=task)
            return
        
    for role, participants in smt_group['groups']['DEFAULT'].items():
        if role in extended_groups:
            if 'account_owner' in event:
                if event['account_owner'].lower() not in participants['Resp']:
                    participants['Resp'].insert(0, event['account_owner'])
            responsible = find_key("responsible", event)
            if responsible:
                if responsible['login'].lower() not in participants['Resp']:
                    participants['Resp'].insert(0, responsible['login'])
        post_data = {
            'GroupName': smt_group['group_name_prefix'] + str(account_id)
                         + "-" + cloudaccount_id + role,
            'ADGroupType': smt_group['adgroup_type'],
            'RegionName': smt_group['region_name'],
            'LocationName' : smt_group['location_name'],
            'GroupUnit': "Groups",
            'ContainerName':smt_group['container_name'],
            'Resps': participants['Resp']
            }
        print(post_data)
        if 'Members' in participants:
            post_data['ToAddMembers'] = participants['Members']
        if smt_group['account_type'] == 'Azure':
            post_data['ShouldSyncToAzure'] = True
        post_response = requests.post(url=smt_rest_uri + "/CreateGroup", json=post_data,verify=False, auth=("{}".format("auto\\uidu700z"), "x6S8Mty4PD"), proxies=proxy)
        print(post_response.reason)

    for role, participants in smt_group['groups'][division].items():
        if role in extended_groups:
            if 'account_owner' in event:
                if event['account_owner'].lower() not in participants['Resp']:
                    participants['Resp'].insert(0, event['account_owner'])
            responsible = find_key("responsible", event)
            if responsible:
                if responsible['login'].lower() not in participants['Resp']:
                    participants['Resp'].insert(0, responsible['login'])
        post_data = {
            'GroupName': smt_group['group_name_prefix'] + str(account_id)
                         + "-" + cloudaccount_id + role,
            'ADGroupType': smt_group['adgroup_type'],
            'RegionName': smt_group['region_name'],
            'LocationName': smt_group['location_name'],
            'GroupUnit': "Groups",
            'ContainerName': smt_group['container_name'],
            'Resps': participants['Resp']
            }
        if 'Members' in participants:
            post_data['ToAddMembers'] = participants['Members']
        if smt_group['account_type'] == 'Azure':
            post_data['ShouldSyncToAzure'] = True
        post_response = requests.post(url=smt_rest_uri + "/CreateGroup", json=post_data,verify=False, auth=("{}".format("auto\\uidu700z"), "x6S8Mty4PD"), proxies=proxy)
        print(post_response.reason)
    
    if ("task" in event):
        time = "{}".format(datetime.now())
        
        if smt_group['account_type'] == 'Azure':
            task['parameters']['account_id'] = account_id
            task['tasks'][str(current_task)]['created_at'] = time
        else:
            if smt_group['account_type'] == 'Alibaba':
                account_id = find_key("account_id", event)
            task['parameters']['account_id'] = account_id
            task['tasks'][str(current_task)]['completed'] = True
            task['tasks'][str(current_task)]['created_at'] = time
            task['current_task'] = int(current_task + 1)
            task['tasks'][str(current_task)]['completed_at'] = time
        dynamodb.Table("jobs").put_item(Item=task)
        print(task)