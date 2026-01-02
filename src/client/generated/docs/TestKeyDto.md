# TestKeyDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**integration_id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**url** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.test_key_dto import TestKeyDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestKeyDto from a JSON string
test_key_dto_instance = TestKeyDto.from_json(json)
# print the JSON string representation of the object
print(TestKeyDto.to_json())

# convert the object into a dict
test_key_dto_dict = test_key_dto_instance.to_dict()
# create an instance of TestKeyDto from a dict
test_key_dto_from_dict = TestKeyDto.from_dict(test_key_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


