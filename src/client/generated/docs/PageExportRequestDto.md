# PageExportRequestDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content** | [**List[ExportRequestDto]**](ExportRequestDto.md) |  | [optional] 
**empty** | **bool** |  | [optional] 
**first** | **bool** |  | [optional] 
**last** | **bool** |  | [optional] 
**number** | **int** |  | [optional] 
**number_of_elements** | **int** |  | [optional] 
**pageable** | [**Pageable**](Pageable.md) |  | [optional] 
**size** | **int** |  | [optional] 
**sort** | [**PageAccessGroupDtoSort**](PageAccessGroupDtoSort.md) |  | [optional] 
**total_elements** | **int** |  | [optional] 
**total_pages** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.page_export_request_dto import PageExportRequestDto

# TODO update the JSON string below
json = "{}"
# create an instance of PageExportRequestDto from a JSON string
page_export_request_dto_instance = PageExportRequestDto.from_json(json)
# print the JSON string representation of the object
print(PageExportRequestDto.to_json())

# convert the object into a dict
page_export_request_dto_dict = page_export_request_dto_instance.to_dict()
# create an instance of PageExportRequestDto from a dict
page_export_request_dto_from_dict = PageExportRequestDto.from_dict(page_export_request_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


