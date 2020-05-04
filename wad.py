"""                 _
                | |
 _ _ _ _____  __| |  ____  _   _
| | | (____ |/ _  | |  _ \| | | |
| | | / ___ ( (_| |_| |_| | |_| |
 \___/\_____|\____(_)  __/ \__  |
                    |_|   (____/

A small script for listing and exporting WhatsApp chat sessions.
Exporting group chats is not supported (yet).
The ChatStorage.sqlite must be in the same directory.

Usage:
    wad.py dump [--dms | --groups]
    wad.py sessions
    wad.py -h | --help

Options:
    -h --help          Shows this help message
"""

import pandas as pd
import sqlite3
import json
import os
from datetime import datetime

from docopt import docopt


############################################
#   DEFINE BASIC FUNCTIONS AND VARIABLES   #
############################################

def get_df(table):
    con = sqlite3.connect('ChatStorage.sqlite')
    df = pd.read_sql_query(("SELECT * from " + str(table)), con)
    con.close()
    return df

get_df_by_sid = lambda df, sid: df[df.ZCHATSESSION == sid]
timestamp_to_apple = lambda x: (datetime.fromtimestamp(x) + (datetime(2001,1,1) - datetime(1970, 1, 1))).strftime('%d %B %Y - %H:%M')

chats = get_df('ZWAMESSAGE')
sessions = get_df('ZWACHATSESSION')[get_df('ZWACHATSESSION')['ZSESSIONTYPE'] != 3]
sessions = sessions[sessions['ZFLAGS'] != 1304].reset_index()

################################
#   DEFINE COMMAND FUNCTIONS   #
################################

def df_to_JSON(df):
    return json.loads(df[['ZISFROMME', 'ZMESSAGEDATE', 'ZPUSHNAME', 'ZTEXT', 'ZMEDIAITEM', 'ZMESSAGETYPE']].to_json(orient='records'))

def export_to_TXT():
    for index, session in sessions.iterrows():
        chat = df_to_JSON(get_df_by_sid(chats, session['Z_PK']))
        partner = session['ZPARTNERNAME']
        dir = os.getcwd() + '\\chats\\'
        with open(dir + session['ZPARTNERNAME'] + '.txt', 'w+', encoding='utf-8') as file:
            for message in chat:
                if message['ZISFROMME'] == 0 and not message['ZTEXT'] and not message['ZMEDIAITEM'] or message['ZMESSAGETYPE'] == 6:
                    continue
                if message['ZTEXT'] and message['ZMEDIAITEM']:
                    msg = f"[ MEDIA ] {message['ZTEXT']}"
                elif message['ZMEDIAITEM']:
                    msg = "[ MEDIA ]"
                else:
                    msg = message['ZTEXT']

                if session['ZSESSIONTYPE'] == 1:
                    partner = message['ZPUSHNAME']

                author = partner if message['ZPUSHNAME'] else "Me"
                file.write(f'[{timestamp_to_apple(message["ZMESSAGEDATE"])}] {author}: {msg}\n')

def getChats():
    dm_list = []
    group_list = []

    # Get sessions
    for index, row in sessions.iterrows():
        if row['ZSESSIONTYPE'] == 1:
            glist = {}
            glist['sid'] = row['Z_PK']
            glist['name'] = row['ZPARTNERNAME']
            glist['messages'] = str(row['ZMESSAGECOUNTER'])
            ppname = get_df('ZWAPROFILEPUSHNAME')
            memberlist = []
            for index, member in get_df_by_sid(get_df('ZWAGROUPMEMBER'), row['Z_PK']).iterrows():
                member_id = member['ZMEMBERJID']
                for i, r in ppname.iterrows():
                    if r['ZJID'] == member_id:
                        member_id = r['ZPUSHNAME']
                        break
                memberlist.append(member_id)
            glist['members'] = memberlist
            group_list.append(glist)
        elif row['ZSESSIONTYPE'] == 0:
            slist = {}
            slist['sid'] = row['Z_PK']
            slist['name'] = row['ZPARTNERNAME']
            slist['number'] = "+{} {}".format(row['ZCONTACTJID'].split('@')[0][:2],row['ZCONTACTJID'].split('@')[0][2:])
            slist['messages'] = str(row['ZMESSAGECOUNTER'])
            dm_list.append(slist)
    return {'dm': dm_list, 'group': group_list}

def list_all():
    chats = getChats()
    dms = chats['dm']
    groups = chats['group']
    for group in groups:
        group['members'] = ', '.join(group['members'])
    print(f'\n[ Found {len(dms)} DMs and {len(groups)} group chats. ]\n')
    print('DMs:')
    print(pd.DataFrame(dms).to_string(index=False))
    print('\nGroup Chats:')
    print(pd.DataFrame(groups).to_string(index=False))


######################
#   INITIALIZATION   #
######################

if __name__ == '__main__':
    args = docopt(__doc__, version='WhatsAppDump 2.0.0-dev')
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)

    if args['sessions']:
        list_all()
    elif args['dump']:
        export_to_TXT()
