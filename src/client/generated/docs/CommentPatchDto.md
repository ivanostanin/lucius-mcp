# CommentPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**body** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.comment_patch_dto import CommentPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of CommentPatchDto from a JSON string
comment_patch_dto_instance = CommentPatchDto.from_json(json)
# print the JSON string representation of the object
print(CommentPatchDto.to_json())

# convert the object into a dict
comment_patch_dto_dict = comment_patch_dto_instance.to_dict()
# create an instance of CommentPatchDto from a dict
comment_patch_dto_from_dict = CommentPatchDto.from_dict(comment_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


