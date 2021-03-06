#!/usr/bin/env python3 -u

### Copyright 2016 Steven J. Murdoch 
### 
### Licensed under the Apache License, Version 2.0 (the "License");
### you may not use this file except in compliance with the License.
### You may obtain a copy of the License at
### 
###     http://www.apache.org/licenses/LICENSE-2.0
### 
### Unless required by applicable law or agreed to in writing, software
### distributed under the License is distributed on an "AS IS" BASIS,
### WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
### See the License for the specific language governing permissions and
### limitations under the License.

import sys
import re
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import colorama
from colorama import Fore, Back, Style
colorama.init()

RE_C2S = re.compile(r'Received\[c2s(?:\_unauthed)?\]\[((?:"[^"]*?")|-)\]: "([^"]*?)"')

def parse_line(line):
    line = line.strip()
    logmessage = line.split("\t", 3)[-1]
    match = RE_C2S.match(logmessage)
    if match:
        if match.group(1)=="-":
            sender = None
        else:
            sender = match.group(1)[1:-1]
        message = match.group(2)

        mt = ET.fromstring(message)
        if mt.tag == "message":
            recipient = mt.attrib.get("to", None)
            body = mt.find("body")
            print('{: <40}'.format(sender) + " \u2192 " + '{: >40}'.format(recipient), end=": ")
            if body.text.startswith("?OTR"):
                print(Fore.RED + "encrypted" + Style.RESET_ALL)
            else:
                body = ET.tostring(body)
                pb = BeautifulSoup(body, "html.parser")
                print(Fore.CYAN + pb.get_text() + Style.RESET_ALL)
        elif mt.tag == "iq":
            data = mt.find(".//*[@type='submit']")
            if data:
                values = data.findall(".//{jabber:x:data}value")
                print("Register: " + Fore.GREEN + "/".join([v.text for v in values]) + Style.RESET_ALL)


def main():
    if len(sys.argv) < 2 or sys.argv[1]=="-":
        fh = sys.stdin
    else:
        fh = open(sys.argv[1], "r")

    for line in fh:
        try:
            parse_line(line)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise

if __name__=="__main__":
    main()
