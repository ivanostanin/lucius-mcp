# JobTestCasesStatDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job** | [**JobDto**](JobDto.md) |  | [optional] 
**test_cases_count** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.job_test_cases_stat_dto import JobTestCasesStatDto

# TODO update the JSON string below
json = "{}"
# create an instance of JobTestCasesStatDto from a JSON string
job_test_cases_stat_dto_instance = JobTestCasesStatDto.from_json(json)
# print the JSON string representation of the object
print(JobTestCasesStatDto.to_json())

# convert the object into a dict
job_test_cases_stat_dto_dict = job_test_cases_stat_dto_instance.to_dict()
# create an instance of JobTestCasesStatDto from a dict
job_test_cases_stat_dto_from_dict = JobTestCasesStatDto.from_dict(job_test_cases_stat_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


