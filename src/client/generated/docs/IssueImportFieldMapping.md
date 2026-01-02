# IssueImportFieldMapping


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**integration_id** | **int** |  | 
**items_separator** | **str** |  | [optional] 
**regex** | **bool** |  | [optional] 

## Example

```python
from src.client.generated.models.issue_import_field_mapping import IssueImportFieldMapping

# TODO update the JSON string below
json = "{}"
# create an instance of IssueImportFieldMapping from a JSON string
issue_import_field_mapping_instance = IssueImportFieldMapping.from_json(json)
# print the JSON string representation of the object
print(IssueImportFieldMapping.to_json())

# convert the object into a dict
issue_import_field_mapping_dict = issue_import_field_mapping_instance.to_dict()
# create an instance of IssueImportFieldMapping from a dict
issue_import_field_mapping_from_dict = IssueImportFieldMapping.from_dict(issue_import_field_mapping_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


