# CommentDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**body** | **str** |  | [optional] 
**body_html** | **str** |  | [optional] 
**created_by** | **str** |  | [optional] 
**created_date** | **int** |  | [optional] 
**first_name** | **str** |  | [optional] 
**id** | **int** |  | [optional] 
**last_modified_by** | **str** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**last_name** | **str** |  | [optional] 
**test_case_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.comment_dto import CommentDto

# TODO update the JSON string below
json = "{}"
# create an instance of CommentDto from a JSON string
comment_dto_instance = CommentDto.from_json(json)
# print the JSON string representation of the object
print(CommentDto.to_json())

# convert the object into a dict
comment_dto_dict = comment_dto_instance.to_dict()
# create an instance of CommentDto from a dict
comment_dto_from_dict = CommentDto.from_dict(comment_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


