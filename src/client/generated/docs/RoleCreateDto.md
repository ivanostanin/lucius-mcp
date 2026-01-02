# RoleCreateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 

## Example

```python
from src.client.generated.models.role_create_dto import RoleCreateDto

# TODO update the JSON string below
json = "{}"
# create an instance of RoleCreateDto from a JSON string
role_create_dto_instance = RoleCreateDto.from_json(json)
# print the JSON string representation of the object
print(RoleCreateDto.to_json())

# convert the object into a dict
role_create_dto_dict = role_create_dto_instance.to_dict()
# create an instance of RoleCreateDto from a dict
role_create_dto_from_dict = RoleCreateDto.from_dict(role_create_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


