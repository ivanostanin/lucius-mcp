# MuteCreateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**issues** | [**List[IssueDto]**](IssueDto.md) |  | [optional] 
**name** | **str** |  | [optional] 
**reason** | **str** |  | [optional] 
**test_case_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.mute_create_dto import MuteCreateDto

# TODO update the JSON string below
json = "{}"
# create an instance of MuteCreateDto from a JSON string
mute_create_dto_instance = MuteCreateDto.from_json(json)
# print the JSON string representation of the object
print(MuteCreateDto.to_json())

# convert the object into a dict
mute_create_dto_dict = mute_create_dto_instance.to_dict()
# create an instance of MuteCreateDto from a dict
mute_create_dto_from_dict = MuteCreateDto.from_dict(mute_create_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


