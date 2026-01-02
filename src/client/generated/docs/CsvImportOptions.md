# CsvImportOptions


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**auto_detect_format** | **bool** |  | [optional] 
**column_separator** | **str** |  | [optional] 
**escape_char** | **str** |  | [optional] 
**quote_char** | **str** |  | [optional] 
**with_headers** | **bool** |  | [optional] 

## Example

```python
from src.client.generated.models.csv_import_options import CsvImportOptions

# TODO update the JSON string below
json = "{}"
# create an instance of CsvImportOptions from a JSON string
csv_import_options_instance = CsvImportOptions.from_json(json)
# print the JSON string representation of the object
print(CsvImportOptions.to_json())

# convert the object into a dict
csv_import_options_dict = csv_import_options_instance.to_dict()
# create an instance of CsvImportOptions from a dict
csv_import_options_from_dict = CsvImportOptions.from_dict(csv_import_options_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


