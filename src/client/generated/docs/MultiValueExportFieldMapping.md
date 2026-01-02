# MultiValueExportFieldMapping


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_field** | **object** |  | [optional] 
**name** | **str** |  | [optional] 
**items_separator** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.multi_value_export_field_mapping import MultiValueExportFieldMapping

# TODO update the JSON string below
json = "{}"
# create an instance of MultiValueExportFieldMapping from a JSON string
multi_value_export_field_mapping_instance = MultiValueExportFieldMapping.from_json(json)
# print the JSON string representation of the object
print(MultiValueExportFieldMapping.to_json())

# convert the object into a dict
multi_value_export_field_mapping_dict = multi_value_export_field_mapping_instance.to_dict()
# create an instance of MultiValueExportFieldMapping from a dict
multi_value_export_field_mapping_from_dict = MultiValueExportFieldMapping.from_dict(multi_value_export_field_mapping_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


