"""A script for exporting and listing WhatsApp chats. At the moment, 
the ChatStorage.sqlite has to be exported into the same directory.
This script does not export group chats (yet).

Usage:
    wad.py dump_chat [<output>] [(--all | --single <sid>)]
    wad.py sessions   
    wad.py -h | --help

Options:
    --all              Export every chat (Default)
    --single <sid>     Exports a single given chat session
    -h --help          Shows this help message
    --about            Shows the about info
"""

from docopt import docopt
import pandas as pd
import sqlite3, os
from datetime import datetime
from yattag import Doc


##############################
#   DEFINE BASIC FUNCTIONS   #
##############################

def get_df(table):
    con = sqlite3.connect('ChatStorage.sqlite')
    df = pd.read_sql_query(("SELECT * from " + str(table)), con)
    con.close()
    return df

get_df_by_sid = lambda df, sid: df[df.ZCHATSESSION == sid]
timestamp_to_apple = lambda x: (datetime.fromtimestamp(x) + (datetime(2001,1,1) - datetime(1970, 1, 1))).strftime('%d %B %Y - %H:%M')


################################
#   DEFINE COMMAND FUNCTIONS   #
################################

def dump_chats(output, sid):
    df = get_df('ZWAMESSAGE')
    chat_list = get_df('ZWACHATSESSION')[~get_df('ZWACHATSESSION').ZCONTACTJID.str.contains('g.us')]
    
    # Setup yattag, generate HTML
    doc, tag, text, line = Doc().ttl()

    doc.asis('<!DOCTYPE html>')

    def generate_html(df):
        for index, row in df.iterrows():
            with tag('html'):
                with tag('head'):
                    doc.asis('<link rel="stylesheet" href="style.css">')
                with tag('body'):
                    with tag('header'):
                        line('h1', df.ZPUSHNAME[df.ZPUSHNAME.first_valid_index()])
                    with tag('main'):
                        for index, row in df.iterrows():
                            if str(row['ZTEXT']) == 'None':
                                continue
                            elif str(row['ZPUSHNAME']) == 'None':
                                line('p', row['ZTEXT'], ('data-date', timestamp_to_apple(row['ZMESSAGEDATE'])), klass = 'host')
                            else:
                                line('p', row['ZTEXT'], ('data-date', timestamp_to_apple(row['ZMESSAGEDATE'])))
                doc.asis('<script type="text/javascript" src="main.js"')
            return str(doc.getvalue())


    if sid:
        with open(os.getcwd() + '\\WAChats\\' + get_df_by_sid(df, int(sid)).ZPUSHNAME.iloc[0] + '.html', 'w+', encoding='utf-8') as c:
            c.write(generate_html(get_df_by_sid(df, int(sid))))
    else:
        for index, row in chat_list.iterrows():
            with open(os.getcwd() + '\\WAChats\\' + row['ZPARTNERNAME'] + '.html', 'w+', encoding='utf-8') as c:
                c.write(generate_html(get_df_by_sid(df, row['Z_PK'])))


def sessions():
    df = get_df('ZWACHATSESSION')

    df = df[~df.ZCONTACTJID.str.contains('g.us')]
    df['ZCONTACTJID'] = df['ZCONTACTJID'].str.split('@').str[0]
    df = df.rename(columns={'ZPARTNERNAME': 'NAME', 'ZCONTACTJID': 'NUMBER', 'Z_PK': 'SID'})
    
    print(df[['NAME', 'NUMBER', 'SID']])


if __name__ == '__main__':
    args = docopt(__doc__, version='WhatsAppDump 0.1.0')
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    
    if args['sessions']:
        sessions()
    elif args['dump_chat']:
        if args['--single']:
            dump_chats(args['<output>'], args['--single'])
        else:
            dump_chats(args['<output>'])
