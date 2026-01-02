# TestCaseImportMapping


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_field** | [**TestCaseImportField**](TestCaseImportField.md) |  | 

## Example

```python
from src.client.generated.models.test_case_import_mapping import TestCaseImportMapping

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseImportMapping from a JSON string
test_case_import_mapping_instance = TestCaseImportMapping.from_json(json)
# print the JSON string representation of the object
print(TestCaseImportMapping.to_json())

# convert the object into a dict
test_case_import_mapping_dict = test_case_import_mapping_instance.to_dict()
# create an instance of TestCaseImportMapping from a dict
test_case_import_mapping_from_dict = TestCaseImportMapping.from_dict(test_case_import_mapping_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


