# ExportFieldMappingTestResultExportField


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_field** | [**TestResultExportField**](TestResultExportField.md) |  | [optional] 
**name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.export_field_mapping_test_result_export_field import ExportFieldMappingTestResultExportField

# TODO update the JSON string below
json = "{}"
# create an instance of ExportFieldMappingTestResultExportField from a JSON string
export_field_mapping_test_result_export_field_instance = ExportFieldMappingTestResultExportField.from_json(json)
# print the JSON string representation of the object
print(ExportFieldMappingTestResultExportField.to_json())

# convert the object into a dict
export_field_mapping_test_result_export_field_dict = export_field_mapping_test_result_export_field_instance.to_dict()
# create an instance of ExportFieldMappingTestResultExportField from a dict
export_field_mapping_test_result_export_field_from_dict = ExportFieldMappingTestResultExportField.from_dict(export_field_mapping_test_result_export_field_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


