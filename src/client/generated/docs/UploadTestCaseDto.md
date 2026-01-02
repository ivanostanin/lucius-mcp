# UploadTestCaseDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** |  | [optional] 
**description_html** | **str** |  | [optional] 
**full_name** | **str** |  | [optional] 
**labels** | [**List[UploadLabelDto]**](UploadLabelDto.md) |  | [optional] 
**links** | [**List[UploadLinkDto]**](UploadLinkDto.md) |  | [optional] 
**name** | **str** |  | 
**parameters** | [**List[UploadParameterDto]**](UploadParameterDto.md) |  | [optional] 
**project_id** | **int** |  | [optional] 
**test_case_id** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.upload_test_case_dto import UploadTestCaseDto

# TODO update the JSON string below
json = "{}"
# create an instance of UploadTestCaseDto from a JSON string
upload_test_case_dto_instance = UploadTestCaseDto.from_json(json)
# print the JSON string representation of the object
print(UploadTestCaseDto.to_json())

# convert the object into a dict
upload_test_case_dto_dict = upload_test_case_dto_instance.to_dict()
# create an instance of UploadTestCaseDto from a dict
upload_test_case_dto_from_dict = UploadTestCaseDto.from_dict(upload_test_case_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


