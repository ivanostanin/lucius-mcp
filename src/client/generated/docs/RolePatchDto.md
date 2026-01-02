# RolePatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.role_patch_dto import RolePatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of RolePatchDto from a JSON string
role_patch_dto_instance = RolePatchDto.from_json(json)
# print the JSON string representation of the object
print(RolePatchDto.to_json())

# convert the object into a dict
role_patch_dto_dict = role_patch_dto_instance.to_dict()
# create an instance of RolePatchDto from a dict
role_patch_dto_from_dict = RolePatchDto.from_dict(role_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


