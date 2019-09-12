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

def list(sid):
    df = get_df('ZWAMESSAGE')

def dump_chats(output, sid):
    df = get_df('ZWAMESSAGE')
    media = get_df('ZWAMEDIAITEM')
    chat_list = get_df('ZWACHATSESSION')[~get_df('ZWACHATSESSION').ZCONTACTJID.str.contains('status')].reset_index() # Hide status messages

    output = os.path.normpath(output)
    
    # Setup yattag, generate HTML

    def generate_html(df):
        is_group_chat = False
        if 'g.us' in df.ZFROMJID[df.ZFROMJID.first_valid_index()]:
            is_group_chat = True
            
        def is_from_me():
            if row['ZPUSHNAME']:
                return False
            else:
                return True
            
        doc, tag, text, line = Doc().ttl()
        doc.asis('<!DOCTYPE html>')
        
        with tag('head'):
            doc.asis('<link rel="stylesheet" href="style.css">')
        with tag('body'):
            with tag('header'):
                line('h1', chat_list['ZPARTNERNAME'][chat_list.Z_PK == df.ZCHATSESSION.iloc[0]].iloc[0])
            with tag('main'):
                for index, row in df.iterrows():
                    if (str(row['ZTEXT']) == 'None') and pd.isna(row['ZMEDIAITEM']):
                        continue
                    elif not pd.isna(row['ZMEDIAITEM']):
                        try:
                            #   AUDIO
                            if '.caf' in media['ZMEDIALOCALPATH'][media.Z_PK == int(row['ZMEDIAITEM'])].iloc[0]:
                                if is_from_me():
                                    line('p', '(Voice Message)', ('data-date', timestamp_to_apple(row['ZMESSAGEDATE'])), klass=('system host' if is_from_me() else 'system'))
                            #   IMAGES
                            elif '.jpg' in media['ZMEDIALOCALPATH'][media.Z_PK == int(row['ZMEDIAITEM'])].iloc[0]:
                                with tag('div', klass=('thumbnail host' if is_from_me() else 'thumbnail')):
                                    doc.stag('img', src=media['ZMEDIALOCALPATH'][media.Z_PK == int(row['ZMEDIAITEM'])].iloc[0].lower().strip('/'), alt='COULD NOT LOAD IMAGE')
                            #   VIDEO
                            elif '.mp4' in media['ZMEDIALOCALPATH'][media.Z_PK == int(row['ZMEDIAITEM'])].iloc[0]:
                                with tag('div', klass=('thumbnail host' if is_from_me() else 'thumbnail')):
                                    with tag('video', controls='true'):
                                        doc.stag('source', src=media['ZMEDIALOCALPATH'][media.Z_PK == int(row['ZMEDIAITEM'])].iloc[0].lower().strip('/'), type='video/mp4')
                                        doc.asis('Your browser does not support videos :(')
                        except TypeError:
                            line('p', 'This message has been deleted', klass='system')
                    elif is_from_me():
                        line('p', row['ZTEXT'], ('data-date', timestamp_to_apple(row['ZMESSAGEDATE'])), klass = 'host')
                    else:
                        line('p', row['ZTEXT'], (('data-from', row['ZPUSHNAME']) if is_group_chat() else ''), ('data-date', timestamp_to_apple(row['ZMESSAGEDATE'])))
        doc.asis('<script type="text/javascript" src="main.js"')
        return str(doc.getvalue())

    # Export to output
    try:
        if sid:
            for s in sid:
                with open(output + '\\' + chat_list['ZPARTNERNAME'][chat_list.Z_PK == int(s)].iloc[0] + ' (' + chat_list['ZCONTACTJID'][chat_list.Z_PK == int(s)].iloc[0].split('@')[0] + ')' + '.html', 'w+', encoding='utf-8') as c:
                    c.write(generate_html(get_df_by_sid(df, int(s))))
                print('Exported chat ' + str(sid.index(s)+1) + '/' + str(len(sid)))
        else:
            for index, row in chat_list.iterrows():
                try:
                    with open(output + '\\' + row['ZPARTNERNAME'] + ' (' + row['ZCONTACTJID'].split('@')[0] + ')' + '.html', 'w+', encoding='utf-8') as c:
                        c.write(generate_html(get_df_by_sid(df, row['Z_PK'])))
                except KeyError:
                    print('Skipped chat #' + str(index+1) + ' (' + str(row['ZPARTNERNAME']) + ')')
                print('Exported chat ' + str(index+1) + '/' + str(len(chat_list)))
        print('Done!')
    except FileNotFoundError:
        print('Uh-oh! Looks like the path you\'ve entered is incorrect... Try again!')
    except KeyboardInterrupt:
        print('\nExport cancelled!')

def sessions():
    df = get_df('ZWACHATSESSION')

    df = df[~df.ZCONTACTJID.str.contains('status')] # Hide status message

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
            dump_chats(os.getcwd(), args['<sid>'])
        elif args['<output>']:
            dump_chats(args['<output>'], args['<sid>'])
