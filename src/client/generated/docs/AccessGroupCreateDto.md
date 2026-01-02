# AccessGroupCreateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**projects** | [**List[AccessGroupProjectAccessDto]**](AccessGroupProjectAccessDto.md) |  | [optional] 
**users** | [**List[NameOnlyDto]**](NameOnlyDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.access_group_create_dto import AccessGroupCreateDto

# TODO update the JSON string below
json = "{}"
# create an instance of AccessGroupCreateDto from a JSON string
access_group_create_dto_instance = AccessGroupCreateDto.from_json(json)
# print the JSON string representation of the object
print(AccessGroupCreateDto.to_json())

# convert the object into a dict
access_group_create_dto_dict = access_group_create_dto_instance.to_dict()
# create an instance of AccessGroupCreateDto from a dict
access_group_create_dto_from_dict = AccessGroupCreateDto.from_dict(access_group_create_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


