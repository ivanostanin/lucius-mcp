# LinkExportFieldMapping


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_field** | **object** |  | [optional] 
**name** | **str** |  | [optional] 
**items_separator** | **str** |  | 

## Example

```python
from src.client.generated.models.link_export_field_mapping import LinkExportFieldMapping

# TODO update the JSON string below
json = "{}"
# create an instance of LinkExportFieldMapping from a JSON string
link_export_field_mapping_instance = LinkExportFieldMapping.from_json(json)
# print the JSON string representation of the object
print(LinkExportFieldMapping.to_json())

# convert the object into a dict
link_export_field_mapping_dict = link_export_field_mapping_instance.to_dict()
# create an instance of LinkExportFieldMapping from a dict
link_export_field_mapping_from_dict = LinkExportFieldMapping.from_dict(link_export_field_mapping_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


