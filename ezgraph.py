import azure.identity
from requests import Session
import argparse
import traceback


session = Session()


def get_credentials() -> azure.identity.AzureCliCredential:
    '''Grabs authentication token from CLI context (run `az login` prior to using script).
    Yes, this is a function just wrapping another function...
    '''
    try:
        creds = azure.identity.AzureCliCredential()
        # Gets an access token to use with Microsoft Graph API
        token = creds.get_token("https://graph.microsoft.com/.default").token
        session.headers = {
            'Content-type': "application/json", 'Authorization': f'{token}'}
    except Exception as err:
        print('Unable to locate credentials - did you try running `az login` in this terminal?')
        traceback.print_exc(err)
        exit()
    return creds, token


def add_user_to_group(user_id, group_id):

    data = {
        "@odata.id": (f'https://graph.microsoft.com/v1.0/directoryObjects/{user_id}')
    }

    r = session.post(
        (f'https://graph.microsoft.com/v1.0/groups/{group_id}/members/$ref'), json=data)
    if r.status_code == 204:
        print("Successfully added user to group")
    else:
        print(r.status_code)
        print(r.text)


def add_Approle_SP(principal_id, resource_id, approle_id):

    data = {}
    data['principalId'] = principal_id
    data['resourceId'] = resource_id
    data['appRoleId'] = approle_id

    r = session.post(
        (f'https://graph.microsoft.com/v1.0/servicePrincipals/{principal_id}/appRoleAssignments'), json=data)
    if r.status_code == 201:
        print("Successfully added app role to service principal")
    else:
        print(r.status_code)
        print(r.text)


def add_role(user_id, role_id):
    data = {
        "@odata.id": (f'https://graph.microsoft.com/v1.0/directoryObjects/{user_id}')
    }

    r = session.post(
        (f'https://graph.microsoft.com/v1.0/directoryRoles/roleTemplateId={role_id}/members/$ref'), json=data)

    if r.status_code == 204:
        print("Successfully added role assignment!")
    else:
        print(r.status_code)
        print(r.text)


if __name__ == '__main__':

    role_templates = '''Useful Azure AD Role Template IDs:

        Global Administrator: "62e90394-69f5-4237-9190-012177145e10"
        Application Administrator: "9b895d92-2cd3-44c7-9d02-a6ac2d5ea5c3"
        Cloud Application Administrator: "158c047a-c907-4556-b7ef-446551a6b5f7"
        Exchange Administrator: "29232cdf-9323-42fd-ade2-1d097af3e4de"
        Helpdesk Administrator: "729827e3-9c14-49f7-bb1b-9608f156bbb8"
        Authentication Administrator: "c4e39bd9-1100-46d3-8c65-fb160da0071f"

        To find a full list of default role template ID's, visit "https://docs.microsoft.com/en-us/azure/active-directory/roles/permissions-reference"'''

    app_role_templates = '''Useful Microsoft Graph AppRoles:

        RoleManagement.ReadWrite.Directory (Read/Write all RBAC settings. Warning: Extremely powerful, proceed with caution.): "9e3f62cf-ca93-4989-b6ce-bf83c28f9fe8"
        AppRoleAssignment.ReadWrite.All (Warning: Extremely powerful, proceed with caution): "06b708a9-e830-4db3-a914-8e69da51d44f"
        Directory.ReadWrite.All: "19dbc75e-c2e2-444c-a770-ec69d8559fc7"

        To find a more complete list, visit "https://github.com/mandiant/Mandiant-Azure-AD-Investigator/blob/master/MandiantAzureADInvestigator.json"

    '''

    parser = argparse.ArgumentParser('EzGraph', 'python3 ezgraph.py -h')
    parser._positionals.title = "Available Modules"
    switch = parser.add_subparsers(dest='command')

    add_to_group = switch.add_parser(
        "add_to_group", help="Add a user to a group. Requires one of the following permissions: GroupMember.ReadWrite.All, Group.ReadWrite.All, or Directory.ReadWrite.All. NOTE: If the group is role-assignable, you also need RoleManagement.ReadWrite.Directory. ")
    add_approle_sp = switch.add_parser("add_approle_sp", help="Assign a Microsoft Graph App Role (API Permissions) to a service principal. Requires AppRoleAssignment.ReadWrite.All.",
                                       epilog=app_role_templates, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_AAD_role = switch.add_parser("add_AAD_role", help="Assign an Azure AD Role to an object. Requires RoleManagement.ReadWrite.Directory.",
                                     epilog=role_templates, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_secret_sp = switch.add_parser(
        "add_secret_sp", help="Creates a new secret for app registration (service principal). Requires Application.ReadWrite.OwnedBy or Application.ReadWrite.All.")

    add_to_group.add_argument('-u', '--userId', required=True, default=None,
                              help='Object ID of the user you want to add into a group ')
    add_to_group.add_argument('-g', '--groupId', required=True, default=None,
                              help='Object ID of the group you want to add a user into ')

    add_approle_sp.add_argument('-p', '--principalId', required=True, default=None,
                                help='The id of the  service principal to which you are assigning the app role.')
    add_approle_sp.add_argument('-r', '--resourceId', required=True, default=None,
                                help='The id of the GraphAggregatorService unique to your tenant')
    add_approle_sp.add_argument('-a', '--approleId', required=True, default=None,
                                help='The id of the appRole to assign to the service principal.')

    add_AAD_role.add_argument('-u', '--userId', required=True, default=None,
                              help='Object ID of the user you want to assign a role to')
    add_AAD_role.add_argument('-r', '--roleId', required=True, default=None,
                              help='Azure AD Role Template ID of the role you want to assign.')

    add_secret_sp.add_argument('-i', '--appId', required=True, default=None,
                               help='The application id of the service principal to which you are adding a new secret to.')
    add_secret_sp.add_argument('-d', '--displayName', required=True,
                               default=None, help='The display name to assign your new secret')

    args = parser.parse_args()

    if args.command == None:
        print("Error: use a module or use -h/--help to see help")

    if args.command == "add_to_group":
        get_credentials()
        add_user_to_group(args.userId, args.groupId)

    elif args.command == "add_approle_sp":
        get_credentials()
        add_Approle_SP(args.principalId, args.resourceId, args.approleId)

    elif args.command == "add_AAD_role":
        get_credentials()
        add_role(args.userId, args.roleId)
