# CommentCreateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**body** | **str** |  | 
**test_case_id** | **int** |  | 

## Example

```python
from src.client.generated.models.comment_create_dto import CommentCreateDto

# TODO update the JSON string below
json = "{}"
# create an instance of CommentCreateDto from a JSON string
comment_create_dto_instance = CommentCreateDto.from_json(json)
# print the JSON string representation of the object
print(CommentCreateDto.to_json())

# convert the object into a dict
comment_create_dto_dict = comment_create_dto_instance.to_dict()
# create an instance of CommentCreateDto from a dict
comment_create_dto_from_dict = CommentCreateDto.from_dict(comment_create_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


