# AccessGroupUserDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**username** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.access_group_user_dto import AccessGroupUserDto

# TODO update the JSON string below
json = "{}"
# create an instance of AccessGroupUserDto from a JSON string
access_group_user_dto_instance = AccessGroupUserDto.from_json(json)
# print the JSON string representation of the object
print(AccessGroupUserDto.to_json())

# convert the object into a dict
access_group_user_dto_dict = access_group_user_dto_instance.to_dict()
# create an instance of AccessGroupUserDto from a dict
access_group_user_dto_from_dict = AccessGroupUserDto.from_dict(access_group_user_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


