# AccessGroupProjectAccessDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**permission_set_id** | **int** |  | 
**project_id** | **int** |  | 

## Example

```python
from src.client.generated.models.access_group_project_access_dto import AccessGroupProjectAccessDto

# TODO update the JSON string below
json = "{}"
# create an instance of AccessGroupProjectAccessDto from a JSON string
access_group_project_access_dto_instance = AccessGroupProjectAccessDto.from_json(json)
# print the JSON string representation of the object
print(AccessGroupProjectAccessDto.to_json())

# convert the object into a dict
access_group_project_access_dto_dict = access_group_project_access_dto_instance.to_dict()
# create an instance of AccessGroupProjectAccessDto from a dict
access_group_project_access_dto_from_dict = AccessGroupProjectAccessDto.from_dict(access_group_project_access_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


