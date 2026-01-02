# TestCaseParameterValues


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**values** | **List[str]** |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_parameter_values import TestCaseParameterValues

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseParameterValues from a JSON string
test_case_parameter_values_instance = TestCaseParameterValues.from_json(json)
# print the JSON string representation of the object
print(TestCaseParameterValues.to_json())

# convert the object into a dict
test_case_parameter_values_dict = test_case_parameter_values_instance.to_dict()
# create an instance of TestCaseParameterValues from a dict
test_case_parameter_values_from_dict = TestCaseParameterValues.from_dict(test_case_parameter_values_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


