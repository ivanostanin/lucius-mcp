# AssignRequestDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**username** | **str** |  | 

## Example

```python
from src.client.generated.models.assign_request_dto import AssignRequestDto

# TODO update the JSON string below
json = "{}"
# create an instance of AssignRequestDto from a JSON string
assign_request_dto_instance = AssignRequestDto.from_json(json)
# print the JSON string representation of the object
print(AssignRequestDto.to_json())

# convert the object into a dict
assign_request_dto_dict = assign_request_dto_instance.to_dict()
# create an instance of AssignRequestDto from a dict
assign_request_dto_from_dict = AssignRequestDto.from_dict(assign_request_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


