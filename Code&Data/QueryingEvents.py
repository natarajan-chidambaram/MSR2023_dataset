import requests
import os
import pandas as pd
from tqdm import tqdm
import datetime
from datetime import timedelta
import time
import json
import numpy as np

bot_accounts = pd.read_csv('GroundTruthData/BotAccounts.csv', index_col = [0])
human_accounts = pd.read_csv("GroundTruthData/HumanAccounts.csv", index_col = [0])

bot_accounts['type_GT'] = 'bot'
human_accounts['type_GT'] = 'human'
all_accounts = pd.concat([bot_accounts, human_accounts]).reset_index().drop('index', axis=1).rename(columns = {'login_name':'login'})

#Query GitHub API
QUERY_ROOT = "https://api.github.com"
ACCOUNT = '' # account
TOKEN = '' # GitHub token

def time_to_pause(nextResetTime):
    '''
    To calculate the time that is required to pause querying in case of limit exceed situation
    
    args:
        nextResetTime (str/int): Next reset time for the corresponding API key in the form of timestamp
    
    returns:
        timeDiff (float): The time that is remaining for the next reset to happen. This is the time (in seconds) that the script needs to wait/sleep
        ResetTime (datetime.datetime): The time at which the next reset happens
    '''
    ResetTime = datetime.datetime.fromtimestamp(int(nextResetTime)).strftime('%Y-%m-%d %H:%M:%S')
    ResetTime = datetime.datetime.strptime(ResetTime, '%Y-%m-%d %H:%M:%S')
    timeDiff = (ResetTime - datetime.datetime.now()).total_seconds() + 120
    return timeDiff, ResetTime
    
def unpackJson(json_response):
    '''
    Unpacks the json response (queried data using GitHub REST API for an user account) into a dictionary with the key as json 
    key and value as its corresponding json value

    args:
        json_response (json): The json response (max 100) obtained by querying the data using GitHub REST API for an user account

    returns:
        events (list): List of dictionaries, where each dictionary contains the details corresponding to each event done 
                       by an account and present in the json response
    '''
    
    events = []
    for jr in range(len(json_response)):
        info_dict = {}
        commit_dict = {}
        event_type = json_response[jr].get('type')
        info_dict['event_id'] = json_response[jr].get('id')
        info_dict['event_type'] = json_response[jr].get('type')
        info_dict['login'] = json_response[jr].get('actor', {}).get('login')
        info_dict['repository'] = json_response[jr].get('repo', {}).get('name')
        info_dict['created_at'] = json_response[jr].get('created_at')
        if(event_type == "PushEvent"):
            info_dict['commit_size'] = json_response[jr].get('payload', {}).get('size')
            info_dict['commit_distinct_size'] = json_response[jr].get('payload', {}).get('distinct_size')
            info_dict['ref'] = json_response[jr].get('payload', {}).get('ref')
            info_dict['head_sha'] = json_response[jr].get('payload', {}).get('head')
            info_dict['push_id'] = json_response[jr].get('payload', {}).get('push_id')
        
        elif(event_type == 'PullRequestReviewEvent' or event_type == 'PullRequestEvent' or event_type == 'PullRequestReviewCommentEvent'):
            info_dict['action'] = json_response[jr].get('payload', {}).get('action')
            info_dict['PR_number'] = json_response[jr].get('payload', {}).get('pull_request', {}).get('number')
            info_dict['title'] = json_response[jr].get('payload', {}).get('pull_request', {}).get('title')
            info_dict['state'] = json_response[jr].get('payload', {}).get('pull_request', {}).get('state')
            info_dict['PR_node_id'] = json_response[jr].get('payload', {}).get('pull_request', {}).get('node_id')
            
            if(event_type == 'PullRequestEvent'):
                info_dict['merged'] = json_response[jr].get('payload', {}).get('pull_request', {}).get('merged')
            
            elif(event_type == 'PullRequestReviewCommentEvent'):
                info_dict['comment'] = json_response[jr].get('payload', {}).get('comment', {}).get('body')
                info_dict['comment_node_id'] = json_response[jr].get('payload', {}).get('comment',{}).get('node_id')
                info_dict['comment_created_at'] = json_response[jr].get('payload', {}).get('comment', {}).get('created_at')
                info_dict['comment_updated_at'] = json_response[jr].get('payload', {}).get('comment', {}).get('updated_at')
            
            elif(event_type == 'PullRequestReviewEvent'):
                info_dict['review'] = json_response[jr].get('payload', {}).get('review', {}).get('body')
                info_dict['review_submitted_at'] = json_response[jr].get('payload', {}).get('review', {}).get('submitted_at')
                info_dict['review_state'] = json_response[jr].get('payload', {}).get('review', {}).get('state')
                info_dict['review_node_id'] = json_response[jr].get('payload', {}).get('review', {}).get('node_id')
            
            info_dict['body'] = json_response[jr].get('payload', {}).get('pull_request', {}).get('body')
            info_dict['draft'] = json_response[jr].get('payload', {}).get('pull_request', {}).get('draft')
            info_dict['PR_created_at'] = json_response[jr].get('payload', {}).get('pull_request', {}).get('created_at')
            info_dict['PR_updated_at'] = json_response[jr].get('payload', {}).get('pull_request', {}).get('updated_at')
            info_dict['PR_merged_at'] = json_response[jr].get('payload', {}).get('pull_request', {}).get('merged_at')
            info_dict['PR_closed_at'] = json_response[jr].get('payload', {}).get('pull_request', {}).get('closed_at')
            info_dict['merge_commit_sha'] = json_response[jr].get('payload', {}).get('pull_request', {}).get('merge_commit_sha')
            if(json_response[jr].get('payload', {}).get('pull_request', {}).get('labels')):
                label = ''
                for l in range(len(json_response[jr].get('payload', {}).get('pull_request', {}).get('labels'))):
                    temp_label = json_response[jr].get('payload', {}).get('pull_request', {}).get('labels', {})[l].get('name')
                    label = f'{label}, {temp_label}'
                info_dict['label'] = label
            
            if(json_response[jr].get('payload', {}).get('pull_request', {}).get('head', {}).get('repo')):
                info_dict['repo_primary_branch'] = json_response[jr].get('payload', {}).get('pull_request', 
                                                                                            {}).get('head', {}).get('repo', {}).get('default_branch')
                info_dict['PR_created_from'] = json_response[jr].get('payload', {}).get('pull_request', 
                                                                                            {}).get('head', {}).get('repo', {}).get('full_name')
                info_dict['PR_created_by'] = json_response[jr].get('payload', {}).get('pull_request', 
                                                                                            {}).get('head', {}).get('user', {}).get('login')
            info_dict['PR_created_from'] = json_response[jr].get('payload', {}).get('pull_request', {}).get('head', {}).get('ref')
            info_dict['PR_created_to'] = json_response[jr].get('payload', {}).get('pull_request', {}).get('based', {}).get('ref')
            info_dict['num_commits'] = json_response[jr].get('payload', {}).get('pull_request', {}).get('commits')
            info_dict['num_comments'] = json_response[jr].get('payload', {}).get('pull_request', {}).get('comments')
            info_dict['num_review_comments'] = json_response[jr].get('payload', {}).get('pull_request', {}).get('review_comments')
            info_dict['num_changed_files'] = json_response[jr].get('payload', {}).get('pull_request', {}).get('changed_files')
            
            if(info_dict['action'] == 'closed' and info_dict['merged'] == True):
                info_dict['manual_PR_decision'] = 'accepted'
            elif(info_dict['action'] == 'closed' and info_dict['merged'] == False):
                info_dict['manual_PR_decision'] = 'rejected' #can be accepted from external source 
        
        elif(event_type == 'IssueCommentEvent' or event_type == 'IssuesEvent'):
            
            if('/pull/' in json_response[jr].get('payload').get('issue', {}).get('html_url')):
                info_dict['PR_number'] = json_response[jr].get('payload', {}).get('issue', {}).get('number')
                info_dict['draft'] = json_response[jr].get('payload', {}).get('issue', {}).get('draft')
                info_dict['PR_merged_at'] = json_response[jr].get('payload', {}).get('issue', {}).get('pullrequest', {}).get('merged_at')
            else:
                info_dict['issue_number'] = json_response[jr].get('payload', {}).get('issue', {}).get('number')
            info_dict['action'] = json_response[jr].get('payload', {}).get('action')
            info_dict['title'] = json_response[jr].get('payload', {}).get('issue', {}).get('title')
            info_dict['state'] = json_response[jr].get('payload', {}).get('issue', {}).get('state')
            info_dict['body'] = json_response[jr].get('payload', {}).get('issue', {}).get('body')
            info_dict['issue_node_id'] = json_response[jr].get('payload', {}).get('issue', {}).get('node_id')
            info_dict['issue_created_at'] = json_response[jr].get('payload', {}).get('issue', {}).get('created_at')
            info_dict['issue_updated_at'] = json_response[jr].get('payload', {}).get('issue', {}).get('updated_at')
            info_dict['issue_closed_at'] = json_response[jr].get('payload', {}).get('issue', {}).get('closed_at')
            info_dict['close_reason'] = json_response[jr].get('payload', {}).get('issue', {}).get('state_reason')
            info_dict['num_comments'] = json_response[jr].get('payload', {}).get('issue', {}).get('comments')
            
            if(json_response[jr].get('payload', {}).get('issue', {}).get('labels')):
                label = ''
                for l in range(len(json_response[jr].get('payload', {}).get('issue', {}).get('labels'))):
                    temp_label = json_response[jr].get('payload', {}).get('issue', {}).get('labels', {})[l].get('name')
                    label = f'{label};{temp_label}'
                info_dict['label'] = label
            if(event_type == 'IssueCommentEvent'):
                info_dict['comment'] = json_response[jr].get('payload', {}).get('comment',{}).get('body')
                info_dict['comment_node_id'] = json_response[jr].get('payload', {}).get('comment',{}).get('node_id')
                info_dict['comment_created_at'] = json_response[jr].get('payload', {}).get('comment',{}).get('created_at')
                info_dict['comment_updated_at'] = json_response[jr].get('payload', {}).get('comment',{}).get('updated_at')
        
        elif(event_type == 'DeleteEvent' or event_type == 'CreateEvent'):
            info_dict['ref'] = json_response[jr].get('payload', {}).get('ref')
            info_dict['ref_type'] = json_response[jr].get('payload', {}).get('ref_type')
            if(event_type == 'CreateEvent'):
                info_dict['tag_description'] = json_response[jr].get('payload', {}).get('description')
        
        elif(event_type == 'CommitCommentEvent'):
            info_dict['body'] = json_response[jr].get('payload', {}).get('comment', {}).get('body')
            info_dict['comment_node_id'] = json_response[jr].get('payload', {}).get('comment', {}).get('node_id')
            info_dict['commit_id'] = json_response[jr].get('payload', {}).get('comment', {}).get('commit_id')
            info_dict['comment_created_at'] = json_response[jr].get('payload', {}).get('created_at')
            info_dict['commit_updated_at'] = json_response[jr].get('payload', {}).get('updated_at')
            if(json_response[jr].get('payload', {}).get('created_at') == json_response[jr].get('payload', {}).get('updated_at')):
                info_dict['action'] = 'created'
            else:
                info_dict['action'] = 'updated'
        
        elif(event_type == 'ForkEvent'):
            info_dict['forked_repository'] = json_response[jr].get('repo', {}).get('name')
            info_dict['forked_as'] = json_response[jr].get('payload', {}).get('forkee', {}).get('full_name')
            info_dict['body'] = json_response[jr].get('payload', {}).get('description')
            info_dict['open_issues_count'] = json_response[jr].get('payload', {}).get('open_issues_count')
            info_dict['action'] = 'forked'
        
        elif(event_type == 'GollumEvent'):
            for p in range(len(json_response[jr].get('payload', {}).get('pages'))):
                info_dict['action'] = json_response[jr].get('payload', {}).get('pages', {})[p].get('action')
                info_dict['page_name'] = json_response[jr].get('payload', {}).get('pages', {})[p].get('page_name')
                info_dict['page_title'] = json_response[jr].get('payload', {}).get('pages', {})[p].get('title')
                info_dict['wiki_sha'] = json_response[jr].get('payload', {}).get('pages', {})[p].get('sha')
        
        elif(event_type == 'MemberEvent'):
            info_dict['action'] = json_response[jr].get('payload', {}).get('action')
            info_dict['member_name'] = json_response[jr].get('payload', {}).get('member', {}).get('login')
        
        elif(event_type == 'ReleaseEvent'):
            info_dict['action'] = json_response[jr].get('payload', {}).get('action')
            info_dict['author'] = json_response[jr].get('payload', {}).get('release', {}).get('author', {}).get('login')
            info_dict['draft'] = json_response[jr].get('payload', {}).get('release', {}).get('draft')
            info_dict['prerelease'] = json_response[jr].get('payload', {}).get('release', {}).get('prerelease')
            info_dict['tag_name'] = json_response[jr].get('payload', {}).get('release', {}).get('tag_name')
            info_dict['description'] = json_response[jr].get('payload', {}).get('release', {}).get('body')
            info_dict['release_created_at'] = json_response[jr].get('payload', {}).get('release', {}).get('created_at')
            info_dict['release_published_at'] = json_response[jr].get('payload', {}).get('release', {}).get('published_at')
            info_dict['release_name'] = json_response[jr].get('payload', {}).get('release', {}).get('name')
            info_dict['release_node_id'] = json_response[jr].get('payload', {}).get('release', {}).get('node_id')
        
        elif(event_type == 'WatchEvent'):
            info_dict['action'] = json_response[jr].get('payload', {}).get('action')
        events.append(info_dict)
    return(events)

'''
Collect contributor event information (last 300 events that were made in the past 90 days) using GitHub API 
'''

login_details = all_accounts['login'].to_list()

list_event = []
list_commit_event = []

#Creating a folder to store the Raw data
folder_name = datetime.datetime.now().strftime('Data_%Y_%m_%d_%H_%M_%S')
os.mkdir('RawData')
os.mkdir(f'RawData/{folder_name}')
f = open(f'RawData/{folder_name}/log.txt', 'w+')

f.write(f'There are {len(login_details)} accounts present in the collection')
time_before_query = datetime.datetime.now()
for login_name in tqdm(login_details):
    page = 1
    while(page < 4):
        try:
            query = f'{QUERY_ROOT}/users/{login_name}/events?per_page=100&page={page}'
            query_session = requests.Session()
            query_session.auth = (ACCOUNT, TOKEN)
            response = query_session.get(query)

            if response.ok:
                json_response = response.json()
                if not json_response and page == 1:
                    info_dict = {}
                    info_dict['event_id'] = None
                    info_dict['event_type'] = None
                    info_dict['commit_url'] = None
                    info_dict['login'] = login_name
                    info_dict['display_name'] = None
                    info_dict['repository'] = None
                    info_dict['created_at'] = None
                    list_event.append(info_dict)
                    break #breaking the while loop if the event list is empty
                
                events = unpackJson(json_response)
                list_event.extend(events)
                
                file_name = f'RawData/{folder_name}/{login_name}_{page}.json'
                with open(file_name, 'w') as file_object:
                    json.dump(json_response, file_object)
                
                if(len(json_response) == 100):
                    page = page + 1
                else:
                    break #breaking the while loop if less than 100 events are recorded in a page - No need to go to next page
                
                if int(response.headers['X-RateLimit-Remaining']) < 5:
                    pause, ResetTime = time_to_pause(int(response.headers['X-RateLimit-Reset']))
                    f.write(str("Limit exceeded. Querying paused until next reset time: {0}".format(ResetTime)))
                    time.sleep(pause)
            else:
                break
        
        except requests.exceptions.Timeout as e:
            f.write('Timeout happened')
            f.write(e)
#             print(e)
            time.sleep(60)
        except requests.ConnectionError as e:
            f.write('Connection error occurred')
            f.write(e)
#             print(e)
            time.sleep(10)

df_events_obt = pd.DataFrame.from_dict(list_event, orient = 'columns')

time_after_query = datetime.datetime.now()
time_for_query = time_after_query - time_before_query
f.write(f'\nTime for query - {time_for_query}')

'''
Data summary
'''
dups = df_events_obt[df_events_obt.duplicated()].groupby('login')['event_type'].count().to_dict()
f.write(str('\nThere are {0} total events obtained through query, among which {1} are duplicated and caused by {2}'.format(df_events_obt.shape[0], df_events_obt[df_events_obt.duplicated()].shape[0], dups)))

'''
Merging the acquired data with original dataset with login_name as primary key so that the account details and their url can be 
mapped and this would be the principal dataframe
'''
df_events_obt_GT = (
    pd.merge(df_events_obt, all_accounts, left_on=df_events_obt['login'].str.lower(), right_on=all_accounts['login'].str.lower(), how='inner')
    .drop(['key_0', 'login_y'], axis=1)
    .rename(columns={'login_x':'login'})
)

df_events = df_events_obt_GT.drop_duplicates()

login_group = (
    df_events
    .groupby(['login','event_id'], as_index = False) # pushevents with 'n' commits have a cardinality of 'n' 
                                                     # with same eventid, so groupby events id then on login gives the num of 
                                                     # events by that login
    .count()
    .groupby(['login'], as_index = False)
    .count()
    [['login', 'event_type']] # each commit in pushevent has a sepearte row, so the event id is same for all the commits in the 
                        # same pushevent. Adding merge_commit_sha will be another primary key
    .rename(columns = {'event_type': 'num_events'})
)
event_type_null = df_events_obt_GT[df_events_obt_GT['event_type'].isnull()].groupby(['login', 'type_GT'], as_index=False).count()
event_type_notnull = df_events_obt_GT[df_events_obt_GT['event_type'].notnull()].groupby(['login', 'type_GT'], as_index=False).count()

f.write(str('\nOut of the {0} accounts queried, query is successfull for {1} accounts. {2} accounts have at least one \
activity (human: {3}, bot: {4}), and {5} accounts have no activity (human: {6}, bot: {7}) in the past 90 days'.format(len(login_details), len(df_events_obt_GT.groupby('login').count()), len(login_group), len(event_type_notnull.query('type_GT == "human"')), len(event_type_notnull.query('type_GT == "bot"')), len(event_type_null), len(event_type_null.query('type_GT == "human"')), len(event_type_null.query('type_GT == "bot"')))))

temp = pd.merge(df_events_obt, all_accounts, left_on=df_events_obt['login'].str.lower(), right_on=all_accounts['login'].str.lower(), how='inner')
acc_failed_query = (
    temp
    .groupby('key_0', as_index=False)
    .count()
    .rename(columns = {'key_0': 'temp_col'})['temp_col']
    .append(all_accounts['login'].str.lower())
    .drop_duplicates(keep = False)
    .values
)
f.write(str('\naccount that failed in query: {0}'.format(acc_failed_query)))

f.write(str('\nunique number of events by bot: {0}'.format(len(df_events.query('type_GT == "bot"')['event_type'].unique()))))
f.write(str('\nEvents done by bots: {0}'.format(df_events.query('type_GT == "bot"')['event_type'].sort_values().unique())))
f.write(str('\nunique number of events by human: {0}'.format(len(df_events.query('type_GT == "human"')['event_type'].unique()))))
f.write(str('\nEvents done by humans: {0}'.format(df_events.query('type_GT == "human"')['event_type'].sort_values().unique())))


f.write(str(df_events.shape))

'''
Save the queried data in the form of a DataFrame in the corresponding folder containing the Rawdata_new
'''
df_events[df_events['event_type'].notnull()].to_csv(f'RawData/{folder_name}/EventsCollectionDetailed.csv')

f.close()