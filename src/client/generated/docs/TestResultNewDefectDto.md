# TestResultNewDefectDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** |  | [optional] 
**issue** | [**IssueToCreateDto**](IssueToCreateDto.md) |  | [optional] 
**link_issue** | [**DefectIssueLinkDto**](DefectIssueLinkDto.md) |  | [optional] 
**matcher** | [**TestResultDefectMatcherDto**](TestResultDefectMatcherDto.md) |  | [optional] 
**name** | **str** |  | 

## Example

```python
from src.client.generated.models.test_result_new_defect_dto import TestResultNewDefectDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestResultNewDefectDto from a JSON string
test_result_new_defect_dto_instance = TestResultNewDefectDto.from_json(json)
# print the JSON string representation of the object
print(TestResultNewDefectDto.to_json())

# convert the object into a dict
test_result_new_defect_dto_dict = test_result_new_defect_dto_instance.to_dict()
# create an instance of TestResultNewDefectDto from a dict
test_result_new_defect_dto_from_dict = TestResultNewDefectDto.from_dict(test_result_new_defect_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


