# TestResultLinkDefectDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**matcher** | [**TestResultDefectMatcherDto**](TestResultDefectMatcherDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.test_result_link_defect_dto import TestResultLinkDefectDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestResultLinkDefectDto from a JSON string
test_result_link_defect_dto_instance = TestResultLinkDefectDto.from_json(json)
# print the JSON string representation of the object
print(TestResultLinkDefectDto.to_json())

# convert the object into a dict
test_result_link_defect_dto_dict = test_result_link_defect_dto_instance.to_dict()
# create an instance of TestResultLinkDefectDto from a dict
test_result_link_defect_dto_from_dict = TestResultLinkDefectDto.from_dict(test_result_link_defect_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


