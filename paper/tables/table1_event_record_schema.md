| field | required | description |
| --- | --- | --- |
| event_id | yes | Unique event identifier used as the graph event key. |
| event_type | yes | Controlled event category used by matching and update rules. |
| subject | yes | Primary entity participating in the event. |
| object | yes | Secondary entity or value-bearing object of the event. |
| time | yes | ISO date string used for temporal matching. |
| trigger | yes | Trigger phrase associated with the event record. |
| evidence_span | yes | Text span that must appear in the source text. |
| source_doc_id | yes | Identifier of the source document or controlled sample. |
| record_id | no | Optional stream record identifier. |
| stream_record_id | no | Optional replay stream record identifier. |
| base_event_id | no | Optional base event used for perturbation grouping. |
| gold_group_id | no | Optional group identifier in the controlled stream. |
| arrival_index | no | Optional replay ordering index. |
| perturbation_type | no | Optional controlled perturbation family. |
| expected_operator | no | Optional expected graph update operator. |
| source_text | no | Optional source text used by evidence matching. |
| temporal_shuffle | no | Optional flag for temporal replay perturbations. |
