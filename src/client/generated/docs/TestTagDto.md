# TestTagDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.test_tag_dto import TestTagDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestTagDto from a JSON string
test_tag_dto_instance = TestTagDto.from_json(json)
# print the JSON string representation of the object
print(TestTagDto.to_json())

# convert the object into a dict
test_tag_dto_dict = test_tag_dto_instance.to_dict()
# create an instance of TestTagDto from a dict
test_tag_dto_from_dict = TestTagDto.from_dict(test_tag_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


