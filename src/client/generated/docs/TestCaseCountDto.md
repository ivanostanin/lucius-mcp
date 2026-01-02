# TestCaseCountDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_count_dto import TestCaseCountDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseCountDto from a JSON string
test_case_count_dto_instance = TestCaseCountDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseCountDto.to_json())

# convert the object into a dict
test_case_count_dto_dict = test_case_count_dto_instance.to_dict()
# create an instance of TestCaseCountDto from a dict
test_case_count_dto_from_dict = TestCaseCountDto.from_dict(test_case_count_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


