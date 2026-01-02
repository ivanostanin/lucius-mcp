# TestCaseVersionRqDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** |  | [optional] 
**title** | **str** |  | 

## Example

```python
from src.client.generated.models.test_case_version_rq_dto import TestCaseVersionRqDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseVersionRqDto from a JSON string
test_case_version_rq_dto_instance = TestCaseVersionRqDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseVersionRqDto.to_json())

# convert the object into a dict
test_case_version_rq_dto_dict = test_case_version_rq_dto_instance.to_dict()
# create an instance of TestCaseVersionRqDto from a dict
test_case_version_rq_dto_from_dict = TestCaseVersionRqDto.from_dict(test_case_version_rq_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


