# TestCaseUpdateSchemaDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_field** | [**TestCaseUpdateFieldDto**](TestCaseUpdateFieldDto.md) |  | [optional] 
**id** | **int** |  | [optional] 
**policy** | [**TestCaseUpdatePolicyDto**](TestCaseUpdatePolicyDto.md) |  | [optional] 
**project_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_update_schema_dto import TestCaseUpdateSchemaDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseUpdateSchemaDto from a JSON string
test_case_update_schema_dto_instance = TestCaseUpdateSchemaDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseUpdateSchemaDto.to_json())

# convert the object into a dict
test_case_update_schema_dto_dict = test_case_update_schema_dto_instance.to_dict()
# create an instance of TestCaseUpdateSchemaDto from a dict
test_case_update_schema_dto_from_dict = TestCaseUpdateSchemaDto.from_dict(test_case_update_schema_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


