# whatsapp_chat_dump
A small script for listing and exporting WhatsApp chat sessions into a readable HTML-File. It can now export
* Texts,
* Images and
* Videos.

If requested, I will add voice message support aswell.

## NOTICE
As of now, I am working on a rewrite, which includes several new features, including
* Export to JSON, HTML, TXT, etc.
* Support for texts, imagesm, videos and voice messages
* Support for group chats
* Support for Hyperlinks
* ... and more.

Since I'm working on it in my free time, there is no fixed date for when it will be finished.

## Important
This project requires the following modules:
* Docopt
* Pandas
* Yattag

Furthermore, **the ChatStorage.sqlite file (the WhatsApp Chat database) and the media folder** must be in the same directory.

## Usage
```
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
```
