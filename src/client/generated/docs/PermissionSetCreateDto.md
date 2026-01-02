# PermissionSetCreateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**permissions** | [**List[PermissionDto]**](PermissionDto.md) |  | 

## Example

```python
from src.client.generated.models.permission_set_create_dto import PermissionSetCreateDto

# TODO update the JSON string below
json = "{}"
# create an instance of PermissionSetCreateDto from a JSON string
permission_set_create_dto_instance = PermissionSetCreateDto.from_json(json)
# print the JSON string representation of the object
print(PermissionSetCreateDto.to_json())

# convert the object into a dict
permission_set_create_dto_dict = permission_set_create_dto_instance.to_dict()
# create an instance of PermissionSetCreateDto from a dict
permission_set_create_dto_from_dict = PermissionSetCreateDto.from_dict(permission_set_create_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


