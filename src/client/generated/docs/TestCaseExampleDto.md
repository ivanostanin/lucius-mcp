# TestCaseExampleDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**parameters** | [**List[ParameterValueDto]**](ParameterValueDto.md) |  | [optional] 
**status** | [**TestStatus**](TestStatus.md) |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_example_dto import TestCaseExampleDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseExampleDto from a JSON string
test_case_example_dto_instance = TestCaseExampleDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseExampleDto.to_json())

# convert the object into a dict
test_case_example_dto_dict = test_case_example_dto_instance.to_dict()
# create an instance of TestCaseExampleDto from a dict
test_case_example_dto_from_dict = TestCaseExampleDto.from_dict(test_case_example_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


