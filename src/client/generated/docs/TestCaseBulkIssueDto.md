# TestCaseBulkIssueDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**issues** | [**List[IssueDto]**](IssueDto.md) |  | 
**selection** | [**TestCaseTreeSelectionDto**](TestCaseTreeSelectionDto.md) |  | 

## Example

```python
from src.client.generated.models.test_case_bulk_issue_dto import TestCaseBulkIssueDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseBulkIssueDto from a JSON string
test_case_bulk_issue_dto_instance = TestCaseBulkIssueDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseBulkIssueDto.to_json())

# convert the object into a dict
test_case_bulk_issue_dto_dict = test_case_bulk_issue_dto_instance.to_dict()
# create an instance of TestCaseBulkIssueDto from a dict
test_case_bulk_issue_dto_from_dict = TestCaseBulkIssueDto.from_dict(test_case_bulk_issue_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


