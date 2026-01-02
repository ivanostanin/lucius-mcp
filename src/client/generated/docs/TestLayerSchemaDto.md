# TestLayerSchemaDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_by** | **str** |  | [optional] 
**created_date** | **int** |  | [optional] 
**id** | **int** |  | [optional] 
**key** | **str** |  | [optional] 
**last_modified_by** | **str** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**project_id** | **int** |  | [optional] 
**test_layer** | [**TestLayerDto**](TestLayerDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.test_layer_schema_dto import TestLayerSchemaDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestLayerSchemaDto from a JSON string
test_layer_schema_dto_instance = TestLayerSchemaDto.from_json(json)
# print the JSON string representation of the object
print(TestLayerSchemaDto.to_json())

# convert the object into a dict
test_layer_schema_dto_dict = test_layer_schema_dto_instance.to_dict()
# create an instance of TestLayerSchemaDto from a dict
test_layer_schema_dto_from_dict = TestLayerSchemaDto.from_dict(test_layer_schema_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


