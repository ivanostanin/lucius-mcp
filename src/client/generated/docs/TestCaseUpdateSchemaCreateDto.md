# TestCaseUpdateSchemaCreateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_field** | [**TestCaseUpdateFieldDto**](TestCaseUpdateFieldDto.md) |  | [optional] 
**policy** | [**TestCaseUpdatePolicyDto**](TestCaseUpdatePolicyDto.md) |  | [optional] 
**project_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_update_schema_create_dto import TestCaseUpdateSchemaCreateDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseUpdateSchemaCreateDto from a JSON string
test_case_update_schema_create_dto_instance = TestCaseUpdateSchemaCreateDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseUpdateSchemaCreateDto.to_json())

# convert the object into a dict
test_case_update_schema_create_dto_dict = test_case_update_schema_create_dto_instance.to_dict()
# create an instance of TestCaseUpdateSchemaCreateDto from a dict
test_case_update_schema_create_dto_from_dict = TestCaseUpdateSchemaCreateDto.from_dict(test_case_update_schema_create_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


