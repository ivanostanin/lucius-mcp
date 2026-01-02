# TestCaseCfvBulkAddDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**cfv** | [**List[CustomFieldValueWithCfDto]**](CustomFieldValueWithCfDto.md) |  | 
**selection** | [**TestCaseSelectionDtoV2**](TestCaseSelectionDtoV2.md) |  | 

## Example

```python
from src.client.generated.models.test_case_cfv_bulk_add_dto import TestCaseCfvBulkAddDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseCfvBulkAddDto from a JSON string
test_case_cfv_bulk_add_dto_instance = TestCaseCfvBulkAddDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseCfvBulkAddDto.to_json())

# convert the object into a dict
test_case_cfv_bulk_add_dto_dict = test_case_cfv_bulk_add_dto_instance.to_dict()
# create an instance of TestCaseCfvBulkAddDto from a dict
test_case_cfv_bulk_add_dto_from_dict = TestCaseCfvBulkAddDto.from_dict(test_case_cfv_bulk_add_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


