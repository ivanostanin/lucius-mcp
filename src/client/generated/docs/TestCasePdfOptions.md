# TestCasePdfOptions


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**country** | **str** |  | [optional] 
**date_format** | **str** |  | [optional] 
**lang** | **str** |  | [optional] 
**name** | **str** |  | 
**selection** | [**TestCaseTreeSelectionDto**](TestCaseTreeSelectionDto.md) |  | 
**structure** | [**List[TestCasePdfPart]**](TestCasePdfPart.md) |  | [optional] 
**time_zone** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_pdf_options import TestCasePdfOptions

# TODO update the JSON string below
json = "{}"
# create an instance of TestCasePdfOptions from a JSON string
test_case_pdf_options_instance = TestCasePdfOptions.from_json(json)
# print the JSON string representation of the object
print(TestCasePdfOptions.to_json())

# convert the object into a dict
test_case_pdf_options_dict = test_case_pdf_options_instance.to_dict()
# create an instance of TestCasePdfOptions from a dict
test_case_pdf_options_from_dict = TestCasePdfOptions.from_dict(test_case_pdf_options_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


