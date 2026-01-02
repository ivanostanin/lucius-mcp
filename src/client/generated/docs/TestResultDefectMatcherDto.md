# TestResultDefectMatcherDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message_regex** | **str** |  | [optional] 
**name** | **str** |  | 
**trace_regex** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.test_result_defect_matcher_dto import TestResultDefectMatcherDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestResultDefectMatcherDto from a JSON string
test_result_defect_matcher_dto_instance = TestResultDefectMatcherDto.from_json(json)
# print the JSON string representation of the object
print(TestResultDefectMatcherDto.to_json())

# convert the object into a dict
test_result_defect_matcher_dto_dict = test_result_defect_matcher_dto_instance.to_dict()
# create an instance of TestResultDefectMatcherDto from a dict
test_result_defect_matcher_dto_from_dict = TestResultDefectMatcherDto.from_dict(test_result_defect_matcher_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


