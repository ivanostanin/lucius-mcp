# TestCaseBulkNewCfvDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**cfv** | [**List[CustomFieldWithValuesDto]**](CustomFieldWithValuesDto.md) |  | 
**selection** | [**TestCaseTreeSelectionDto**](TestCaseTreeSelectionDto.md) |  | 

## Example

```python
from src.client.generated.models.test_case_bulk_new_cfv_dto import TestCaseBulkNewCfvDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseBulkNewCfvDto from a JSON string
test_case_bulk_new_cfv_dto_instance = TestCaseBulkNewCfvDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseBulkNewCfvDto.to_json())

# convert the object into a dict
test_case_bulk_new_cfv_dto_dict = test_case_bulk_new_cfv_dto_instance.to_dict()
# create an instance of TestCaseBulkNewCfvDto from a dict
test_case_bulk_new_cfv_dto_from_dict = TestCaseBulkNewCfvDto.from_dict(test_case_bulk_new_cfv_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


