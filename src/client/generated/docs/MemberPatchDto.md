# MemberPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.member_patch_dto import MemberPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of MemberPatchDto from a JSON string
member_patch_dto_instance = MemberPatchDto.from_json(json)
# print the JSON string representation of the object
print(MemberPatchDto.to_json())

# convert the object into a dict
member_patch_dto_dict = member_patch_dto_instance.to_dict()
# create an instance of MemberPatchDto from a dict
member_patch_dto_from_dict = MemberPatchDto.from_dict(member_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


