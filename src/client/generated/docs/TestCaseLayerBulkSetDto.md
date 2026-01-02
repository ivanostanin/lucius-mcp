# TestCaseLayerBulkSetDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**layer_id** | **int** |  | [optional] 
**selection** | [**TestCaseSelectionDtoV2**](TestCaseSelectionDtoV2.md) |  | 

## Example

```python
from src.client.generated.models.test_case_layer_bulk_set_dto import TestCaseLayerBulkSetDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseLayerBulkSetDto from a JSON string
test_case_layer_bulk_set_dto_instance = TestCaseLayerBulkSetDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseLayerBulkSetDto.to_json())

# convert the object into a dict
test_case_layer_bulk_set_dto_dict = test_case_layer_bulk_set_dto_instance.to_dict()
# create an instance of TestCaseLayerBulkSetDto from a dict
test_case_layer_bulk_set_dto_from_dict = TestCaseLayerBulkSetDto.from_dict(test_case_layer_bulk_set_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


