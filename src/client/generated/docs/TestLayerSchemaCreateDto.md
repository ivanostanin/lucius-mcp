# TestLayerSchemaCreateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**key** | **str** |  | 
**project_id** | **int** |  | 
**test_layer_id** | **int** |  | 

## Example

```python
from src.client.generated.models.test_layer_schema_create_dto import TestLayerSchemaCreateDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestLayerSchemaCreateDto from a JSON string
test_layer_schema_create_dto_instance = TestLayerSchemaCreateDto.from_json(json)
# print the JSON string representation of the object
print(TestLayerSchemaCreateDto.to_json())

# convert the object into a dict
test_layer_schema_create_dto_dict = test_layer_schema_create_dto_instance.to_dict()
# create an instance of TestLayerSchemaCreateDto from a dict
test_layer_schema_create_dto_from_dict = TestLayerSchemaCreateDto.from_dict(test_layer_schema_create_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


