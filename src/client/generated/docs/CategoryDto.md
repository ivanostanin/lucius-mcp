# CategoryDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**color** | **str** |  | [optional] 
**created_by** | **str** |  | [optional] 
**created_date** | **int** |  | [optional] 
**description** | **str** |  | [optional] 
**id** | **int** |  | [optional] 
**last_modified_by** | **str** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**project_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.category_dto import CategoryDto

# TODO update the JSON string below
json = "{}"
# create an instance of CategoryDto from a JSON string
category_dto_instance = CategoryDto.from_json(json)
# print the JSON string representation of the object
print(CategoryDto.to_json())

# convert the object into a dict
category_dto_dict = category_dto_instance.to_dict()
# create an instance of CategoryDto from a dict
category_dto_from_dict = CategoryDto.from_dict(category_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


