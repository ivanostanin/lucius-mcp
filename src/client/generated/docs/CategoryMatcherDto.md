# CategoryMatcherDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**category** | [**CategoryDto**](CategoryDto.md) |  | [optional] 
**created_by** | **str** |  | [optional] 
**created_date** | **int** |  | [optional] 
**id** | **int** |  | [optional] 
**last_modified_by** | **str** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**message_regex** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**project_id** | **int** |  | [optional] 
**trace_regex** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.category_matcher_dto import CategoryMatcherDto

# TODO update the JSON string below
json = "{}"
# create an instance of CategoryMatcherDto from a JSON string
category_matcher_dto_instance = CategoryMatcherDto.from_json(json)
# print the JSON string representation of the object
print(CategoryMatcherDto.to_json())

# convert the object into a dict
category_matcher_dto_dict = category_matcher_dto_instance.to_dict()
# create an instance of CategoryMatcherDto from a dict
category_matcher_dto_from_dict = CategoryMatcherDto.from_dict(category_matcher_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


