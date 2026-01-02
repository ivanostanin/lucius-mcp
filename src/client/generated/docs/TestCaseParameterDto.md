# TestCaseParameterDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_parameter_dto import TestCaseParameterDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseParameterDto from a JSON string
test_case_parameter_dto_instance = TestCaseParameterDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseParameterDto.to_json())

# convert the object into a dict
test_case_parameter_dto_dict = test_case_parameter_dto_instance.to_dict()
# create an instance of TestCaseParameterDto from a dict
test_case_parameter_dto_from_dict = TestCaseParameterDto.from_dict(test_case_parameter_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


