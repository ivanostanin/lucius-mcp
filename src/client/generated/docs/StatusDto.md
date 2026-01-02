# StatusDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**color** | **str** |  | [optional] 
**created_by** | **str** |  | [optional] 
**created_date** | **int** |  | [optional] 
**id** | **int** |  | [optional] 
**last_modified_by** | **str** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.status_dto import StatusDto

# TODO update the JSON string below
json = "{}"
# create an instance of StatusDto from a JSON string
status_dto_instance = StatusDto.from_json(json)
# print the JSON string representation of the object
print(StatusDto.to_json())

# convert the object into a dict
status_dto_dict = status_dto_instance.to_dict()
# create an instance of StatusDto from a dict
status_dto_from_dict = StatusDto.from_dict(status_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


