# AccessGroupDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**projects_count** | **int** |  | [optional] 
**users** | [**List[AccessGroupUserDto]**](AccessGroupUserDto.md) |  | [optional] 
**users_count** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.access_group_dto import AccessGroupDto

# TODO update the JSON string below
json = "{}"
# create an instance of AccessGroupDto from a JSON string
access_group_dto_instance = AccessGroupDto.from_json(json)
# print the JSON string representation of the object
print(AccessGroupDto.to_json())

# convert the object into a dict
access_group_dto_dict = access_group_dto_instance.to_dict()
# create an instance of AccessGroupDto from a dict
access_group_dto_from_dict = AccessGroupDto.from_dict(access_group_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


