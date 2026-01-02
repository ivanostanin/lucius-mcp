# TestResultParameterDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**excluded** | **bool** |  | [optional] 
**hidden** | **bool** |  | [optional] 
**name** | **str** |  | [optional] 
**value** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.test_result_parameter_dto import TestResultParameterDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestResultParameterDto from a JSON string
test_result_parameter_dto_instance = TestResultParameterDto.from_json(json)
# print the JSON string representation of the object
print(TestResultParameterDto.to_json())

# convert the object into a dict
test_result_parameter_dto_dict = test_result_parameter_dto_instance.to_dict()
# create an instance of TestResultParameterDto from a dict
test_result_parameter_dto_from_dict = TestResultParameterDto.from_dict(test_result_parameter_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


