# GlobalPermissionsDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**project_create** | **bool** |  | [optional] 

## Example

```python
from src.client.generated.models.global_permissions_dto import GlobalPermissionsDto

# TODO update the JSON string below
json = "{}"
# create an instance of GlobalPermissionsDto from a JSON string
global_permissions_dto_instance = GlobalPermissionsDto.from_json(json)
# print the JSON string representation of the object
print(GlobalPermissionsDto.to_json())

# convert the object into a dict
global_permissions_dto_dict = global_permissions_dto_instance.to_dict()
# create an instance of GlobalPermissionsDto from a dict
global_permissions_dto_from_dict = GlobalPermissionsDto.from_dict(global_permissions_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


