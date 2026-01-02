# TestKeySchemaPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**integration_id** | **int** |  | [optional] 
**key** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.test_key_schema_patch_dto import TestKeySchemaPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestKeySchemaPatchDto from a JSON string
test_key_schema_patch_dto_instance = TestKeySchemaPatchDto.from_json(json)
# print the JSON string representation of the object
print(TestKeySchemaPatchDto.to_json())

# convert the object into a dict
test_key_schema_patch_dto_dict = test_key_schema_patch_dto_instance.to_dict()
# create an instance of TestKeySchemaPatchDto from a dict
test_key_schema_patch_dto_from_dict = TestKeySchemaPatchDto.from_dict(test_key_schema_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


