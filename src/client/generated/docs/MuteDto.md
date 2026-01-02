# MuteDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_by** | **str** |  | [optional] 
**created_date** | **int** |  | [optional] 
**id** | **int** |  | [optional] 
**issues** | [**List[IssueDto]**](IssueDto.md) |  | [optional] 
**last_modified_by** | **str** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**reason** | **str** |  | [optional] 
**reason_html** | **str** |  | [optional] 
**test_case_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.mute_dto import MuteDto

# TODO update the JSON string below
json = "{}"
# create an instance of MuteDto from a JSON string
mute_dto_instance = MuteDto.from_json(json)
# print the JSON string representation of the object
print(MuteDto.to_json())

# convert the object into a dict
mute_dto_dict = mute_dto_instance.to_dict()
# create an instance of MuteDto from a dict
mute_dto_from_dict = MuteDto.from_dict(mute_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


