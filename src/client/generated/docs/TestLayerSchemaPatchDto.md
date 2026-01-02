# TestLayerSchemaPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**key** | **str** |  | [optional] 
**test_layer_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.test_layer_schema_patch_dto import TestLayerSchemaPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestLayerSchemaPatchDto from a JSON string
test_layer_schema_patch_dto_instance = TestLayerSchemaPatchDto.from_json(json)
# print the JSON string representation of the object
print(TestLayerSchemaPatchDto.to_json())

# convert the object into a dict
test_layer_schema_patch_dto_dict = test_layer_schema_patch_dto_instance.to_dict()
# create an instance of TestLayerSchemaPatchDto from a dict
test_layer_schema_patch_dto_from_dict = TestLayerSchemaPatchDto.from_dict(test_layer_schema_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


