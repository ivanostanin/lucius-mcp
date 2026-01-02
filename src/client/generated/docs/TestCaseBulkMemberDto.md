# TestCaseBulkMemberDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**members** | [**List[MemberDto]**](MemberDto.md) |  | 
**selection** | [**TestCaseTreeSelectionDto**](TestCaseTreeSelectionDto.md) |  | 

## Example

```python
from src.client.generated.models.test_case_bulk_member_dto import TestCaseBulkMemberDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseBulkMemberDto from a JSON string
test_case_bulk_member_dto_instance = TestCaseBulkMemberDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseBulkMemberDto.to_json())

# convert the object into a dict
test_case_bulk_member_dto_dict = test_case_bulk_member_dto_instance.to_dict()
# create an instance of TestCaseBulkMemberDto from a dict
test_case_bulk_member_dto_from_dict = TestCaseBulkMemberDto.from_dict(test_case_bulk_member_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


