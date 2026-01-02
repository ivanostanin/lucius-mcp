# IssueIntegrationExportFieldMapping


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_field** | **object** |  | [optional] 
**name** | **str** |  | [optional] 
**integration_id** | **int** |  | 
**items_separator** | **str** |  | 

## Example

```python
from src.client.generated.models.issue_integration_export_field_mapping import IssueIntegrationExportFieldMapping

# TODO update the JSON string below
json = "{}"
# create an instance of IssueIntegrationExportFieldMapping from a JSON string
issue_integration_export_field_mapping_instance = IssueIntegrationExportFieldMapping.from_json(json)
# print the JSON string representation of the object
print(IssueIntegrationExportFieldMapping.to_json())

# convert the object into a dict
issue_integration_export_field_mapping_dict = issue_integration_export_field_mapping_instance.to_dict()
# create an instance of IssueIntegrationExportFieldMapping from a dict
issue_integration_export_field_mapping_from_dict = IssueIntegrationExportFieldMapping.from_dict(issue_integration_export_field_mapping_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


