# TestCaseMuteBulkAddDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**mute** | [**MuteDto**](MuteDto.md) |  | 
**selection** | [**TestCaseSelectionDtoV2**](TestCaseSelectionDtoV2.md) |  | 

## Example

```python
from src.client.generated.models.test_case_mute_bulk_add_dto import TestCaseMuteBulkAddDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseMuteBulkAddDto from a JSON string
test_case_mute_bulk_add_dto_instance = TestCaseMuteBulkAddDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseMuteBulkAddDto.to_json())

# convert the object into a dict
test_case_mute_bulk_add_dto_dict = test_case_mute_bulk_add_dto_instance.to_dict()
# create an instance of TestCaseMuteBulkAddDto from a dict
test_case_mute_bulk_add_dto_from_dict = TestCaseMuteBulkAddDto.from_dict(test_case_mute_bulk_add_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


