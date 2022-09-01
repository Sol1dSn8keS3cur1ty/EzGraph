**# EzGraph**

EzGraph is a Python tool used for interacting with Microsoft Graph API. This tool was written for use on offensive engagements (penetration testing), but could be used/modified to fit many purposes. 

 If you're not familiar with Azure, Azure AD and Microsoft Graph, I highly I highly recommend reading [Azure Privilege Escalation via Azure API Permissions Abuse](https://posts.specterops.io/certified-pre-owned-d95910965cd2) by [Andy Robbins](https://medium.com/@_wald0). This blog was really the inspiration for this tool, and  I highly recommend reading all of Andy's work regarding Azure/Azure AD.

## Installation


```bash
pip3 install -r requirements.txt
```

NOTE: Requires Azure CLI to be installed! For help installing Azure CLI, see https://docs.microsoft.com/en-us/cli/azure/install-azure-cli



## Usage

Relies on Azure CLI for authentication - make sure to run az login prior to using the script!
``` az login ``` 

There are currently 3 modules for interacting with various MS Graph endpoints. 

```
usage: python3 ezgraph.py -h

Available Modules:
  {add_to_group,add_approle_sp,add_AAD_role,add_secret_sp}
    add_to_group        Add a user to a group. Requires one of the following permissions: GroupMember.ReadWrite.All,
                        Group.ReadWrite.All, or Directory.ReadWrite.All. NOTE: If the group is role-assignable, you
                        also need RoleManagement.ReadWrite.Directory.
    add_approle_sp      Assign a Microsoft Graph App Role (API Permissions) to a service principal. Requires
                        AppRoleAssignment.ReadWrite.All.
    add_AAD_role        Assign an Azure AD Role to an object. Requires RoleManagement.ReadWrite.Directory.
    
options:
  -h, --help            show this help message and exit
```

### add_to_group

The 'add_to_group' module is used to add a user or service principal into an Azure AD group. Full documentation on this API endpoint can be found [here](https://docs.microsoft.com/en-us/graph/api/group-post-members?view=graph-rest-1.0&tabs=http).

This module requires one of the following API permissions for Microsoft Graph:  
* GroupMember.ReadWrite.All
* Group.ReadWrite.All
* Directory.ReadWrite.All

Potential Privilege Escalation Scenario:  
Add a user or service principal you control into a group that has been assigned elevated privileges within Azure Resource Manager (Contributer, Owner)

Note: If an Azure AD group is role-assignable, meaning it can be assigned an Azure AD role such as "Global Administrator", the permissions listed above will not be sufficient as you will also require the 'RoleManagement.ReadWrite.Directory'. This effectively prevents a principal with the above listed permissions from escalating privileges within Azure AD, however it does not prevent you from escalating privileges within Azure Resource Manager.


```
usage: python3 ezgraph.py -h add_to_group [-h] -u USERID -g GROUPID

options:
  -h, --help            show this help message and exit
  -u USERID, --userId USERID
                        Object ID of the user you want to add into a group
  -g GROUPID, --groupId GROUPID
                        Object ID of the group you want to add a user into
```

### add_approle_sp
The 'add_approle_sp' module is used to assign an API permission (also referreed to as an App Role) to a service principal. Full documentation on this API endpoint can be found [here](https://docs.microsoft.com/en-us/graph/api/serviceprincipal-post-approleassignments?view=graph-rest-1.0&tabs=http).

This module requires  the following API permissions for Microsoft Graph:   
* AppRoleAssignment.ReadWrite.All  
Note: This is a very high privilege for Microsoft Graph. With it, you can assign any API permission you want to any service principal of your choosing. Proceed with caution.

Potential Privilege Escalation Scenario:

```
usage: python3 ezgraph.py -h add_approle_sp [-h] -p PRINCIPALID -r RESOURCEID -a APPROLEID

options:
  -h, --help            show this help message and exit
  -p PRINCIPALID, --principalId PRINCIPALID
                        The id of the service principal to which you are assigning the app role.
  -r RESOURCEID, --resourceId RESOURCEID
                        The id of the GraphAggregatorService unique to your tenant
  -a APPROLEID, --approleId APPROLEID
                        The id of the appRole to assign to the service principal.

Useful Microsoft Graph API Permissions:

        RoleManagement.ReadWrite.Directory (Read/Write all RBAC settings. Warning: Extremely powerful, proceed with caution.): "9e3f62cf-ca93-4989-b6ce-bf83c28f9fe8"
        AppRoleAssignment.ReadWrite.All (Warning: Extremely powerful, proceed with caution): "06b708a9-e830-4db3-a914-8e69da51d44f"
        Directory.ReadWrite.All: "19dbc75e-c2e2-444c-a770-ec69d8559fc7"

        To find a more complete list, visit "https://github.com/mandiant/Mandiant-Azure-AD-Investigator/blob/master/MandiantAzureADInvestigator.json"
```

### add_AAD_role

The "add_AAD_role" module is used to assign an Azure AD role to a user or service principal. Full documentation on tihs API endpoint can be found [here](https://docs.microsoft.com/en-us/graph/api/directoryrole-post-members?view=graph-rest-1.0&tabs=http).

Note: This module uses the "Template ID" method of assigning an Azure AD role.

This module requires the follow API permissions for Microsoft Graph:
* RoleManagement.ReadWrite.Directory
Note: This is essentially the highest permission you can have in Microsoft Graph. With it, you can assign any Azure AD Role to any user or service principal. Proceed with caution.

```
usage: python3 ezgraph.py -h add_AAD_role [-h] -u USERID -r ROLEID

options:
  -h, --help            show this help message and exit
  -u USERID, --userId USERID
                        Object ID of the user you want to assign a role to
  -r ROLEID, --roleId ROLEID
                        Azure AD Role Template ID of the role you want to assign.

Useful Azure AD Role Template IDs:

        Global Administrator: "62e90394-69f5-4237-9190-012177145e10"
        Application Administrator: "9b895d92-2cd3-44c7-9d02-a6ac2d5ea5c3"
        Cloud Application Administrator: "158c047a-c907-4556-b7ef-446551a6b5f7"
        Exchange Administrator: "29232cdf-9323-42fd-ade2-1d097af3e4de"
        Helpdesk Administrator: "729827e3-9c14-49f7-bb1b-9608f156bbb8"
        Authentication Administrator: "c4e39bd9-1100-46d3-8c65-fb160da0071f"

        To find a full list of default role template ID's, visit "https://docs.microsoft.com/en-us/azure/active-directory/roles/permissions-reference"
```

