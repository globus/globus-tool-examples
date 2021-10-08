import argparse
import json
import os
import sys
from globus_sdk import TransferClient
from globus_sdk.services.transfer.errors import TransferAPIError
from fair_research_login.client import NativeClient


CLIENT_ID = "8a31d387-51ab-41ab-9fe0-69184f61d129"
SCOPES = "openid urn:globus:auth:scope:transfer.api.globus.org:all"


def main(source_id, destination_id, prefix):

    # Create a Globus Client
    native_client = NativeClient(
            client_id=CLIENT_ID,
            default_scopes=SCOPES
    )
    native_client.login(no_local_server=True, refresh_tokens=True)
    transfer_authorizer = native_client.get_authorizers().get("transfer.api.globus.org")
    transfer_client = TransferClient(authorizer=transfer_authorizer)

    # List all ACLs
    try:
        resp_acls = transfer_client.endpoint_acl_list(source_id)
    except TransferAPIError as e:
        print(f"ERROR: {e.message}", file=sys.stderr)
        sys.exit(1)

    # Apply all listed ACLs to 'destination' endpoint
    answer = None
    for acl in resp_acls:
        src_path = acl.get("path")
        principal = acl.get("principal")
        permissions = acl.get("permissions")
        if prefix:
            dst_path = os.path.join("/", prefix, src_path.lstrip("/"))
        else:
            dst_path = src_path
        rule_data = {
            "DATA_TYPE": acl.get("DATA_TYPE"),
            "principal_type": acl.get("principal_type"),
            "principal": principal,
            "path": dst_path,
            "permissions": permissions
        }
        print(f"ACL: path {src_path}, user/group {principal}, permissions {permissions}")

        # Check if the path exists on the source endpoint, and warn a user if it does not
        try:
            result = transfer_client.operation_ls(source_id, src_path)
        except TransferAPIError  as e:
            if e.code == "ClientError.NotFound":
                if answer == "S":
                    continue
                if answer != "A":
                    print(f"    Directory {src_path} was not found on the source endpoint. "
                            "Do you want to create a corresponding ACL on the destination endpoint?")
                    answer = input("    (Y) Yes, (N) No, (A) Yes for all ACLs, (S) No for all ACLs with missing paths [default=N]: ")
                    if answer:
                        answer = answer.upper()
                    if answer != "Y" and answer != "A":
                        continue
            else:
                print(f"ERROR: {e.message}", file=sys.stderr)
                sys.exit(1)

        # Check if the path exists on the destination endpoint, and warn a user if it does not
        try:
            result = transfer_client.operation_ls(destination_id, dst_path)
        except TransferAPIError  as e:
            if e.code == "ClientError.NotFound":
                print(f"    Directory {dst_path} was not found on the destination endpoint. The ACL rule will be migrated anyway...")
            else:
                print(f"ERROR: {e.message}", file=sys.stderr)
                sys.exit(1)
        # Create the ACL rule on the destination endpoint
        try:
            result = transfer_client.add_endpoint_acl_rule(destination_id, rule_data)
            print("    The ACL has been migrated")
        except TransferAPIError as e:
            if e.code == "Exists":
                print("    The ACL rule already exists")
            else:
                print(f"ERROR: {e.message}", file=sys.stderr)
                sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate Globus ACLs between Globus endpoints. "
            "The script can be run multiple times without a risk that multiple copies of the same "
            "ACL will be created on an endpoint.")
    parser.add_argument("-s", metavar="UUID", dest="source", required=True,
                        help="source endpoint UUID, e.g. e56c36e4-1063-11e6-a747-22000bf2d559")
    parser.add_argument("-d", metavar="UUID", dest="destination", required=True,
                        help="destination endpoint UUID")
    parser.add_argument("-p", metavar="PREFIX", dest="prefix",
                        help="prefix path - all ACLs created on the destination endpoint will have paths prepended by PREFIX")
    args = parser.parse_args()
    main(args.source, args.destination, args.prefix)
