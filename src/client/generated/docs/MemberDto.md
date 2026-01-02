# MemberDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**role** | [**RoleDto**](RoleDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.member_dto import MemberDto

# TODO update the JSON string below
json = "{}"
# create an instance of MemberDto from a JSON string
member_dto_instance = MemberDto.from_json(json)
# print the JSON string representation of the object
print(MemberDto.to_json())

# convert the object into a dict
member_dto_dict = member_dto_instance.to_dict()
# create an instance of MemberDto from a dict
member_dto_from_dict = MemberDto.from_dict(member_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


