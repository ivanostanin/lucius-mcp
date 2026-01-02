# ExampleExportFieldMapping


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_field** | **object** |  | [optional] 
**name** | **str** |  | [optional] 
**examples_separator** | **str** |  | [optional] 
**name_value_separator** | **str** |  | [optional] 
**params_separator** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.example_export_field_mapping import ExampleExportFieldMapping

# TODO update the JSON string below
json = "{}"
# create an instance of ExampleExportFieldMapping from a JSON string
example_export_field_mapping_instance = ExampleExportFieldMapping.from_json(json)
# print the JSON string representation of the object
print(ExampleExportFieldMapping.to_json())

# convert the object into a dict
example_export_field_mapping_dict = example_export_field_mapping_instance.to_dict()
# create an instance of ExampleExportFieldMapping from a dict
example_export_field_mapping_from_dict = ExampleExportFieldMapping.from_dict(example_export_field_mapping_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


