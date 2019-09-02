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
    wad.py dump_chats [--cd | <output>] [--all | --custom <sid>...]
    wad.py sessions [(find (--name <name> | --number <number>))] [--sort]
    wad.py -h | --help

Examples:
    wad.py dump_chats --custom 7 11 420
    wad.py dump_chats "C:/Users/pixel3rr0r/Documents/Exported Chats"
    wad.py sessions --sort
    wad.py sessions find --name "Niels Bohr"

Options:
    --cd               Exports chats to the current directory (Default)
    --all              Exports every chat (Default)
    --custom           Exports one or more (seperated by space) given chat sessions
    --name             Finds all chat sessions with the given name
    --number           Finds all chat sessions with the given number
    --sid              Finds all chat sessions with the given Session-ID
    --sort             Sorts the list alphabetically
    -h --help          Shows this help message
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
    chat_list = get_df('ZWACHATSESSION')[~get_df('ZWACHATSESSION').ZCONTACTJID.str.contains('g.us')] # Hide group chats

    output = os.path.normpath(output)
    
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

    # Export to output
    try:
        if sid:
            for s in sid:
                with open(output + '\\' + get_df_by_sid(df, int(s)).ZPUSHNAME.iloc[0] + '.html', 'w+', encoding='utf-8') as c:
                    c.write(generate_html(get_df_by_sid(df, int(s))))
                print('Exported chat ' + str(sid.index(s)+1) + '/' + str(len(sid)))
            print('Done!')
        else:
            for index, row in chat_list.iterrows():
                with open(output + '\\' + row['ZPARTNERNAME'] + '.html', 'w+', encoding='utf-8') as c:
                    c.write(generate_html(get_df_by_sid(df, row['Z_PK'])))
                print('Exported chat ' + str(index) + '/' + str(len(chat_list)))
    except FileNotFoundError:
        print('Uh-oh! Looks like the path you\'ve entered is incorrect... Try again!')
    except KeyboardInterrupt:
        print('\nExport cancelled!')

def sessions():
    df = get_df('ZWACHATSESSION')

    df = df[~df.ZCONTACTJID.str.contains('g.us')] # Hide group chats

    # Find chat sessions
    if args['find']:
        if args['--name']:
            df = df[df.ZPARTNERNAME.str.lower().str.contains(args['<name>'].lower())].fillna(False)
            print('Found', len(df), 'chat sessions with', args['<name>'])
        elif args['--number']:
            df = df[df.ZCONTACTJID.str.contains(args['<number>'])].fillna(False)
            print('Found', len(df), 'chat sessions with', args['<number>'])

    if args['--sort']:
        df = df.sort_values(by='ZPARTNERNAME')

    df['ZCONTACTJID'] = df['ZCONTACTJID'].str.split('@').str[0]
    df = df.rename(columns={'ZPARTNERNAME': 'NAME', 'ZCONTACTJID': 'NUMBER', 'Z_PK': 'SID'})

    if not df.empty: print(df[['NAME', 'NUMBER', 'SID']])


######################
#   INITIALIZATION   #
######################

if __name__ == '__main__':
    args = docopt(__doc__, version='WhatsAppDump 1.1.0')
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    
    if args['sessions']:
        sessions()
    elif args['dump_chats']:
        if args['--cd']:
            dump_chats(os.getcwd(), args['sid'])
        else:
            dump_chats(args['<output>'], args['<sid>'])
