# RoleSchemaPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**key** | **str** |  | [optional] 
**role_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.role_schema_patch_dto import RoleSchemaPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of RoleSchemaPatchDto from a JSON string
role_schema_patch_dto_instance = RoleSchemaPatchDto.from_json(json)
# print the JSON string representation of the object
print(RoleSchemaPatchDto.to_json())

# convert the object into a dict
role_schema_patch_dto_dict = role_schema_patch_dto_instance.to_dict()
# create an instance of RoleSchemaPatchDto from a dict
role_schema_patch_dto_from_dict = RoleSchemaPatchDto.from_dict(role_schema_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


