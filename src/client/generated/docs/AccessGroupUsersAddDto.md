# AccessGroupUsersAddDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**usernames** | **List[str]** |  | 

## Example

```python
from src.client.generated.models.access_group_users_add_dto import AccessGroupUsersAddDto

# TODO update the JSON string below
json = "{}"
# create an instance of AccessGroupUsersAddDto from a JSON string
access_group_users_add_dto_instance = AccessGroupUsersAddDto.from_json(json)
# print the JSON string representation of the object
print(AccessGroupUsersAddDto.to_json())

# convert the object into a dict
access_group_users_add_dto_dict = access_group_users_add_dto_instance.to_dict()
# create an instance of AccessGroupUsersAddDto from a dict
access_group_users_add_dto_from_dict = AccessGroupUsersAddDto.from_dict(access_group_users_add_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


