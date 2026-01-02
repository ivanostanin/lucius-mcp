# TestCaseExternalLinkBulkAddDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**links** | [**List[ExternalLinkDto]**](ExternalLinkDto.md) |  | 
**selection** | [**TestCaseSelectionDtoV2**](TestCaseSelectionDtoV2.md) |  | 

## Example

```python
from src.client.generated.models.test_case_external_link_bulk_add_dto import TestCaseExternalLinkBulkAddDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseExternalLinkBulkAddDto from a JSON string
test_case_external_link_bulk_add_dto_instance = TestCaseExternalLinkBulkAddDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseExternalLinkBulkAddDto.to_json())

# convert the object into a dict
test_case_external_link_bulk_add_dto_dict = test_case_external_link_bulk_add_dto_instance.to_dict()
# create an instance of TestCaseExternalLinkBulkAddDto from a dict
test_case_external_link_bulk_add_dto_from_dict = TestCaseExternalLinkBulkAddDto.from_dict(test_case_external_link_bulk_add_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


