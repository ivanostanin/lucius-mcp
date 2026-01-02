# ExpectedBodyStepDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**body** | **str** |  | [optional] 
**body_json** | [**DefaultTextMarkupDocument**](DefaultTextMarkupDocument.md) |  | [optional] 

## Example

```python
from src.client.generated.models.expected_body_step_dto import ExpectedBodyStepDto

# TODO update the JSON string below
json = "{}"
# create an instance of ExpectedBodyStepDto from a JSON string
expected_body_step_dto_instance = ExpectedBodyStepDto.from_json(json)
# print the JSON string representation of the object
print(ExpectedBodyStepDto.to_json())

# convert the object into a dict
expected_body_step_dto_dict = expected_body_step_dto_instance.to_dict()
# create an instance of ExpectedBodyStepDto from a dict
expected_body_step_dto_from_dict = ExpectedBodyStepDto.from_dict(expected_body_step_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


