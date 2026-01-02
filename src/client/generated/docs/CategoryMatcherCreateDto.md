# CategoryMatcherCreateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**category** | [**IdOnlyDto**](IdOnlyDto.md) |  | 
**message_regex** | **str** |  | [optional] 
**name** | **str** |  | 
**project_id** | **int** |  | [optional] 
**trace_regex** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.category_matcher_create_dto import CategoryMatcherCreateDto

# TODO update the JSON string below
json = "{}"
# create an instance of CategoryMatcherCreateDto from a JSON string
category_matcher_create_dto_instance = CategoryMatcherCreateDto.from_json(json)
# print the JSON string representation of the object
print(CategoryMatcherCreateDto.to_json())

# convert the object into a dict
category_matcher_create_dto_dict = category_matcher_create_dto_instance.to_dict()
# create an instance of CategoryMatcherCreateDto from a dict
category_matcher_create_dto_from_dict = CategoryMatcherCreateDto.from_dict(category_matcher_create_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


