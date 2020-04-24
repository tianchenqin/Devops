#!/usr/bin/python

"""
Author: Stefan Scheungrab <stefan.2.scheungrab@continental-corporation.com
create a test job and see what happens
    Parameters: 
        task

"""
import boto3
import boto3.dynamodb.types
import suds
import re
import json
import uuid
from suds.client import Client
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Key, Attr
from html import unescape

def get_contichange_client():
        client = Client('http://hpsm.cw01.contiwan.com:13200/SM/7/contiGenericChangeManagement.wsdl',proxy={'http' : 'http://uidt589z:Windows2000@cias3basic.conti.de:8080'})
        client.set_options(
                proxy={'http' : 'http://uidt589z:Windows2000@cias3basic.conti.de:8080'},
                username='oracle_ws_in',
                password='oracle',
                timeout=20
        )
        return client

def get_change_client():
        client = Client('http://hpsm.cw01.contiwan.com:13200/SM/7/ChangeManagement.wsdl',proxy={'http' : 'http://uidt589z:Windows2000@cias3basic.conti.de:8080'})
        client.set_options(
                proxy={'http' : 'http://uidt589z:Windows2000@cias3basic.conti.de:8080'},
                username='oracle_ws_in',
                password='oracle',
                timeout=20
        )
        return client

def retrieve_change_task(taskid):
        task = get_change_client().service.RetrieveChangeTaskList(
                keys = { 'TaskID' : taskid }
        )
        return task

def retrieve_tasks_by_ci(ci):
        print(ci)
        tasks = get_change_client().service.RetrieveChangeTaskKeysList(
                {
                        'keys' : {},
                        'instance' : {
                                'header' : {
                                        'Status' : 'initial'
                                },
                                'middle' : {
                                        'ConfigurationItem' : ci
                                }
                        }
                }
        )
        return tasks

def retrieve_change_tasklist(changeid):

        tasks = get_change_client().service.RetrieveChangeTaskKeysList(
                {
                        'keys' : {},
                        'instance' : {
                                'header' : {
                                        'ParentChange' : changeid
                                }
                        }
                }
        )
        return tasks

def retrieve_change_task_by_ci(changeid,ci):
        tasks = get_change_client().service.RetrieveChangeTaskKeysList(
                {
                        'keys' : {},
                        'instance' : {
                                'header' : {
                                        'ParentChange' : changeid
                                },
                                'middle' : {
                                        'ConfigurationItem' : ci
                                }
                        }
                }
        )
        return tasks

def remove_empty_from_dict(d):
    if type(d) is dict:
        return dict((k, remove_empty_from_dict(v)) for k, v in d.items() if v and remove_empty_from_dict(v))
    elif type(d) is list:
        return [remove_empty_from_dict(v) for v in d if v and remove_empty_from_dict(v)]
    else:
        return d

def process_change_task(task):
    dynamodb = boto3.resource("dynamodb")
    ##################
    # Prepare the item to be imported to accounts table
    ###
    item = {}
    item['request'] = {}
    item['contacts'] = {}
    item['contacts']['divisional'] = {}
    item['contacts']['responsible'] = {}
    item['contacts']['operational'] = {}
    item['request'] = {}
    item['request']['regions'] = {}
    item['request']['blueprint'] = {}
    item['billing'] = {}
    item['billing']['vat'] = {}
    item['billing']['address'] = {}
    ##################
    changeid = task['instance'][0]['header']['ParentChange'].value
    taskinstance = task.instance[0]
    taskid = taskinstance['header']['TaskID']['value']
    regions = []
    network_speed = {}
    account_description = []
    multiple_requests = ""
    blueprint_azure = [] 
    blueprint = ""
    for description in taskinstance['description.structure']['Description']['Description']:
        try:
            description_line = unescape(description.value)
        except:
            continue
        #regions = []
        #blueprint_azure = []
        # Divisional Contact Information
        if re.match("^Firstname : ",description_line):
            item['contacts']['divisional']['firstname'] = description_line.replace('Firstname : ', '')
        if re.match("^Lastname : ",description_line):
            item['contacts']['divisional']['lastname'] = description_line.replace('Lastname : ', '')
        if re.match("^Phone : ", description_line):
            item['contacts']['divisional']['phone'] = description_line.replace('Phone : ', '')
        if re.match("^eMail : ", description_line):
            item['contacts']['divisional']['mail'] = description_line.replace('eMail : ', '')
        if re.match("^Login ID : ", description_line):  
            item['contacts']['divisional']['login'] = description_line.replace('Login ID : ', '')
        if re.match("^Division : ", description_line):
            item['contacts']['divisional']['division'] = description_line.replace('Division : ', '')
        # Responsible Contact Information
        if re.match("^Responsible Full Name : ", description_line):
            item['contacts']['responsible']['fullname'] = description_line.replace('Responsible Full Name : ', '')
        if re.match("^Responsible Company Name : ", description_line):
            item['contacts']['responsible']['company'] = description_line.replace('Responsible Company Name : ', '')
        if re.match("^Responsible Country : ", description_line):
            item['contacts']['responsible']['country'] = description_line.replace('Responsible Country : ', '')
        if re.match("^Responsible Address : ", description_line):
            item['contacts']['responsible']['address'] = description_line.replace('Responsible Address : ', '')
        if re.match("^Responsible City : ", description_line):
            item['contacts']['responsible']['city'] = description_line.replace('Responsible City : ', '')
        if re.match("^Responsible State / Province or Region : ", description_line):
            item['contacts']['responsible']['provice'] = description_line.replace('Responsible State / Province or Region : ', '')
        if re.match("^Responsible Postal Code : ", description_line):
            item['contacts']['responsible']['postal_code'] = description_line.replace('Responsible Postal Code : ', '')
        if re.match("^Responsible Phone : ", description_line):
            item['contacts']['responsible']['phone'] = description_line.replace('Responsible Phone : ', '')
        if re.match("^Responsible eMail : ", description_line):
            item['contacts']['responsible']['mail'] = description_line.replace('Responsible eMail : ', '')
        if re.match("^Responsible Login ID : ", description_line):
            item['contacts']['responsible']['login'] = description_line.replace('Responsible Login ID : ', '')
        if re.match("^Responsible Division : ", description_line):
            item['contacts']['responsible']['division'] = description_line.replace('Responsible Division : ', '')

        #Operational Conact
        if re.match("^Operation Responsible Full Name : ", desription_line.replace('Operation Responsible Full Name : ', '')
        if re.match("^Operation Responsible Title : ", descrcription_line):
            item['contacts']['operational']['fullname'] = desciption_line):
            item['contacts']['operational']['title'] = description_line.replace('Operation Responsible Title : ', '')
        if re.match("^Operation Responsible eMail Address : ", description_line):
            item['contacts']['operational']['mail'] = description_line.replace('Operation Responsible eMail Address : ', '')
        if re.match("^Operation Responsible Phone Number : ", description_line):
            item['contacts']['operational']['phone'] = description_line.replace('Operation Responsible Phone Number : ', '')

        # Account Type
        if re.match("^Managed Cloud Account : ", description_line):
            item['request']['account_type'] = description_line.replace('Managed Cloud Account : ', '')

        # Organizational Unit for AWS Organizations
        if re.match("^Target OU Structure : ", description_line):
            item['request']['target_ou'] = re.sub('Target OU Structure : ', '',description_line)

        ## Mobility Service
        if re.match("^One Conti Facing account \(default sub OU\) and one Internet facing account \(advanced OU\) will be generated. :", description_line):
            blueprintflat = re.sub('One Conti Facing account.*: ', '',description_line)
            if blueprintflat == "Mobility Services":
                blueprint = "MOBILITY"
                item['request']['blueprint'] = blueprint

        ## Multiple Accounts
        if re.match("^If the checkbox is marked the following 4 accounts will be created (all with the same configuration):<br>[Title]-Dev <br>[Title]-PreLive <br> [Title]-Live <br>[Title]-Backup :", description_line):
            multiple_requests = date_ssp_request = re.sub("If the checkbox is marked the following 4 accounts will be created \(all with the same configuration\):.* : ", "" ,description_line)

        ## Dedicated VPC
        if re.match("^Dedicated VPC : ", description_line):
            item['request']['dedicated_vpc'] = re.sub('Dedicated VPC : ', '',description_line)

        ## VPC Sharing
        if re.match("^VPC Sharing : ", description_line):
            item['request']['vpc_sharing'] = re.sub('VPC Sharing : ', '',description_line)

        # Blueprint
        ## AWS
        if re.match("^Please select your desired blueprint\(s\)<br>If nothing is selected only the account will be generated", description_line):
            blueprintflat = re.sub('Please select your desired blueprint.*: ', '',description_line)
            blueprint = "STORAGE"
            if blueprintflat == "Conti Facing":
                blueprint = "CF"
            if blueprintflat == "Internet Facing":
                blueprint = "IF"
            if blueprintflat == "Conti Facing, Internet Facing":
                blueprint = "CFIF"
            item['request']['blueprint'] = blueprint

        ## AWS 4.06.2019
        if re.match("^Please select your desired blueprint\(s\): : ", description_line):
            blueprintflat = re.sub('Please select your desired blueprint.*: : ', '',description_line)
            blueprint = "STORAGE"
            if blueprintflat == "Conti Facing":
                blueprint = "CF"
            if blueprintflat == "Internet Facing":
                blueprint = "IF"
            if blueprintflat == "Conti Facing, Internet Facing":
                blueprint = "CFIF"
            item['request']['blueprint'] = blueprint

        ## Azure
        if re.match("^Please select your desired VNET\(s\)<br>If nothing is selected only the subscription will be generated", description_line):
            blueprintflat = re.sub('Please select your desired VNET.*: ', '',description_line)
            if "Conti Facing" in blueprintflat:
                blueprint_azure.append("continental")
            if "Internet Facing" in blueprintflat:
                blueprint_azure.append("internet")
            if "Dmz" in blueprintflat:
                blueprint_azure.append("dmz")
            item['request']['blueprint'] = blueprint_azure

        ## Alibaba
        if re.match("^Please select your desired VPC\(s\)<br>If nothing is selected only the account will be generated", description_line):
            blueprintflat = re.sub('Please select your desired VPC.*: ', '',description_line)
            blueprint = "storage"
            if blueprintflat == "Conti Facing":
                blueprint = "continental_facing"
            if blueprintflat == "Internet Facing":
                blueprint = "internet_facing"
            if blueprintflat == "Conti Facing, Internet Facing":
                blueprint = "CFIF"
            item['request']['blueprint'] = blueprint

        #####  AWS ##### 
        # Activate Tagging
        if re.match("^Activate Tagging Enforcement : ", description_line):
            item['request']['tagging_check_active'] = re.sub('Activate Tagging Enforcement : ', '',description_line)

        # OS managed by Corporate
        if re.match("^OS managed by Corporate : ", description_line):
            item['request']['cos_enabled'] = re.sub('OS managed by Corporate : ', '',description_line)

        # Subnet Count / Zone Size
        if re.match("^Availability Zones: : ", description_line):
            item['request']['avail_zones'] =  re.sub('Availability Zones: : ', '',description_line)

        # Subnet Size
        if re.match("^Subnet size: : ", description_line):
            item['request']['zone_size'] = re.sub('Subnet size: : ', '',description_line)

        # Domain Delegation	
        if re.match("^Request DNS Delegation", description_line):
            domain_delegation = re.sub('Request DNS Delegation.*: ', '',description_line)
            if domain_delegation == "Yes":
                item['request']['domain_delegation'] = domain_delegation

        # Dates of SSP
        if re.match("^Date of original SSP Request", description_line):
            date_ssp_request = re.sub('Date of original SSP Request.*: ', '',description_line)
            if date_ssp_request:
                item['request']['date_ssp_request'] = date_ssp_request

        if re.match("^Date of Recipient approval", description_line):
            date_rec_approval = re.sub('Date of Recipient approval.*: ', '',description_line)
            if date_rec_approval:
                item['request']['date_rec_approval'] = date_rec_approval
					        
        if re.match("^Date of security approval", description_line):
            date_sec_approval = re.sub('Date of security approval.*: ', '',description_line)
            if date_sec_approval:
                item['request']['date_sec_approval'] = date_sec_approval

        if re.match("^Date of final approval", description_line):
            date_fin_approval = re.sub('Date of final approval.*: ', '',description_line)
            if date_fin_approval:
                item['request']['date_fin_approval'] = date_fin_approval
							
        # Organizational Unit for AWS Organizations
        if re.match("^Target OU Structure : ", description_line):
            item['request']['target_ou'] = re.sub('Target OU Structure : ', '',description_line)

        # Account Description:
        if re.match("^Account Title : ", description_line):
            account_description_ssp = description_line.replace('Account Title : ', '')
            item['account_description'] = description_line.replace('Account Title : ', '')

        # Regions
        ##AWS
        if re.match("^Region : ", description_line):
            region = description_line.replace('Region : ', '')
            if "Singapore" in region:
                regions.append("ap-southeast-1")
            if "Frankfurt" in region:
                regions.append("eu-central-1")
            if "Auburn Hills" in region:
                regions.append("us-east-1")
            if "Virginia" in region:
                regions.append("us-east-1")
            if not region:
                regions.append("us-east-1")
                regions.append("eu-central-1")
                regions.append("ap-southeast-1")
            item['request']['regions'] = regions

        if re.match("^Asia Pacific \(Singapore\) : ", description_line):
            regionname = "ap-southeast-1"
            speed = re.sub('Asia Pacific \(Singapore\).*: ', '', description_line)
            if "No Connection needed" not in speed:
                item['request']['regions'][regionname] = speed
                network_speed[regionname] = speed
                regions.append("ap-southeast-1")

        if re.match("^EU \(Frankfurt\) : ", description_line):
            regionname = "eu-central-1"
            speed = re.sub('EU \(Frankfurt\).*: ', '', description_line)
            if "No Connection needed" not in speed:
                item['request']['regions'][regionname] = speed
                network_speed[regionname] = speed
                regions.append("eu-central-1")

        if re.match("^US \(N. Virginia\) : ", description_line):
            regionname = "us-east-1"
            speed = re.sub('US \(N. Virginia\).*: ', '', description_line)
            if "No Connection needed" not in speed:
                item['request']['regions'][regionname] = speed
                network_speed[regionname] = speed
                regions.append("us-east-1")

        ## Azure
        # again changes inside the task#
        if re.match("^Which Regions are needed\?  :", description_line):
            if re.match(".*SE Asia \(Singapore\).*", description_line):
                regionname = "southeastasia"
                regions.append(regionname)
                item['request']['regions'] = regions

            if re.match(".*EU West \(Amsterdam\).*", description_line):
                regionname = "westeurope"
                regions.append(regionname)
                item['request']['regions'] = regions

            if re.match(".*US East \(Virginia\).*", description_line):
                regionname = "eastus2"
                regions.append(regionname)
                item['request']['regions'] = regions
         
        #Billing Information
        # Cost Center
        if re.match("^Cost Center : ", description_line):
            item['billing']['cost_center'] = description_line.replace('Cost Center : ', '')

        if re.match("^Cost Center Owner : ", description_line):
            item['billing']['cost_center_owner'] = description_line.replace('Cost Center Owner : ', '')

        # WBS
        if re.match("^WBS \(WorkBreakdownStructure - PSP Element\) : ", description_line):
            item['billing']['wbs'] = re.sub('WBS.*: ', '',description_line)

        # Controller Email
        if re.match("^Controlling contact \(eMail\)", description_line):
            item['billing']['controlling_contact'] = re.sub('Controlling contact.* : ', '',description_line)

        # Billing Comments
        if re.match("^Comment : ", description_line):
            item['billing']['comment'] = description_line.replace('Comment : ', '')

        # Business Legal Name
        if re.match("^Business Legal Name \(Legal Entity\) : ", description_line):
            item['billing']['vat']['legal_entity'] = re.sub('Business Legal Name.*: ', '', description_line)

        # Business Legal Country
        if re.match("^Business Legal Country : ", description_line):
            item['billing']['vat']['country'] = description_line.replace('Business Legal Country : ', '')

        # Consolidation Unit
        if re.match("^Consolidation Unit : ", description_line):
            item['billing']['consolidation_unit'] = description_line.replace('Consolidation Unit : ', '')

        #Store change and task to be closed after the provisioning is finished
        item['request']['changeid'] = changeid
        item['request']['taskid'] = taskid

    if item['request']['account_type']:
        if item['request']['account_type'] == "Azure":
            azure_subtask = retrieve_change_task(retrieve_change_task_by_ci(changeid, "vg_corp_managed_cloud_account")['keys'][0]['TaskID']['value'])
            
            azure_subtask_instance = azure_subtask.instance[0]
            for misc in azure_subtask_instance['middle']['MiscArray1']['MiscArray1']:
                if 'value' in misc:
                    if re.match(".*[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}.*",misc.value):
                        subscription_id = re.sub(r".*([\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}).*", "\\1",misc.value)
                        item['subscription_id'] = subscription_id
                        item['aws_account_id'] = subscription_id

        if item['request']['account_type'] == "Alibaba":
            ali_subtask = retrieve_change_task(retrieve_change_task_by_ci(changeid, "vg_corp_managed_cloud_account")['keys'][0]['TaskID']['value'])
            #ali_subtask = retrieve_change_task("T3078379")
            ali_subtask_instance = ali_subtask.instance[0]
            #print(azure_subtask)
            #print(azure_subtask_instance)
            for misc in ali_subtask_instance['middle']['MiscArray1']['MiscArray1']:
                if 'value' in misc:
                    if re.match(".*[\d]{16}.*",misc.value):
                        alibaba_account_id = re.sub(r".*([\d]{16}).*", "\\1",misc.value)
                        item['alibaba_account_id'] = alibaba_account_id
                        item['aws_account_id'] = alibaba_account_id

        if item['request']['account_type'] == "Amazon":
            if not regions:
                regions.append("us-east-1")
                regions.append("eu-central-1")
                regions.append("ap-southeast-1")
            item['request']['regions'] = regions
            
            if not blueprint:
                blueprint = "STORAGE"
                item['request']['blueprint'] = blueprint
   
        workflow = dynamodb.Table("workflow").get_item(Key={'name': item['request']['account_type']})['Item']
        
        if multiple_requests == "Multiple Accounts":
            account_description.append("{}-Live".format(account_description_ssp))
            account_description.append("{}-PreLive".format(account_description_ssp))
            account_description.append("{}-Dev".format(account_description_ssp))
            account_description.append("{}-Backup".format(account_description_ssp))
        else:
            account_description.append(account_description_ssp)

        for acc_desc in account_description:
            item['account_description'] = acc_desc
            if item['request']['blueprint'] == "MOBILITY" and "{}-Backup".format(account_description_ssp) not in acc_desc:
                item['request']['blueprint'] = "CF"
                job = {
                    'UUID': str(uuid.uuid4()),
                    'status': 'INPROGRESS',
                    'request_trigger': changeid,
                    'completed': False,
                    'parameters': remove_empty_from_dict(item),
                    'tasks': workflow['tasks'],
                    'current_task': 1
                }
                job = dynamodb.Table("jobs").put_item(Item=job)
                print(job)
                item['request']['blueprint'] = "IF"
                job = {
                    'UUID': str(uuid.uuid4()),
                    'status': 'INPROGRESS',
                    'request_trigger': changeid,
                    'completed': False,
                    'parameters': remove_empty_from_dict(item),
                    'tasks': workflow['tasks'],
                    'current_task': 1
                }
                job = dynamodb.Table("jobs").put_item(Item=job)
                print(job)
            else:
                if item['request']['blueprint'] == "MOBILITY":
                    item['request']['blueprint'] = "STORAGE"

                job = {
                    'UUID': str(uuid.uuid4()),
                    'status': 'INPROGRESS',
                    'request_trigger': changeid,
                    'completed': False,
                    'parameters': remove_empty_from_dict(item),
                    'tasks': workflow['tasks'],
                    'current_task': 1
                }
                job = dynamodb.Table("jobs").put_item(Item=job)
                print(job)



def trigger_jobs(event, context):
    dynamodb = boto3.resource("dynamodb")
    ##for task in retrieve_change_tasklist('C1752353')['keys']:
    for task in retrieve_tasks_by_ci('vg_corp_aws_accounts')['keys']:
        if 'value' in task['TaskID']:
            taskid = task['TaskID']['value']
            print(taskid)
            task = retrieve_change_task(taskid)
            changeid =  task['instance'][0]['header']['ParentChange'].value
            job_exists = dynamodb.Table("jobs").scan(FilterExpression=Attr('request_trigger').eq(changeid))['Items']
            if job_exists:
                 # maybe log that the change is already being processed
                continue
            else:
                if "SSP6" not in task['instance'][0]['header']['Originator'].value:
                    continue
                else:
                    process_change_task(task)

    #for task in retrieve_change_tasklist('C1729876')['keys']:
    #for task in retrieve_change_tasklist('C3172729')['keys']:
    for task in retrieve_tasks_by_ci('vg_corp_azure_subscriptions')['keys']:
        print("Azure")
        if 'value' in task['TaskID']:
            taskid = task['TaskID']['value']
            task = retrieve_change_task(taskid)
            changeid =  task['instance'][0]['header']['ParentChange'].value
            job_exists = dynamodb.Table("jobs").scan(FilterExpression=Attr('request_trigger').eq(changeid))['Items']
            if job_exists:
                # maybe log that the change is already being processed
                continue
            else:
                if "SSP6" not in task['instance'][0]['header']['Originator'].value:
                    continue
                else:
                    process_change_task(task)

    #for task in retrieve_change_tasklist('C2623164')['keys']:
    for task in retrieve_tasks_by_ci('vg_corp_alibaba_accounts')['keys']:
        if 'value' in task['TaskID']:
            taskid = task['TaskID']['value']
            task = retrieve_change_task(taskid)
            changeid =  task['instance'][0]['header']['ParentChange'].value
            job_exists = dynamodb.Table("jobs").scan(FilterExpression=Attr('request_trigger').eq(changeid))['Items']
            if job_exists:
                # maybe log that the change is already being processed
                continue
            else:
                if "SSP6" not in task['instance'][0]['header']['Originator'].value:
                    continue
                else:
                    print("before")
                    process_change_task(task)
