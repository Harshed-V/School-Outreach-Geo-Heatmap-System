# School Dataset Import

Place the Tamil Nadu UDISE/SSA school CSV at:

```text
backend/data/tamil_nadu_schools.csv
```

Or set `SCHOOL_DATASET_PATH` in `.env`.

Required fields:

- `school_name`
- `district`

Optional fields:

- `category` or `school_category`
- `student_count`, `students`, or `enrolment`
- `population`
- `urban_index`
- `recent_growth`

The loader accepts common column-name variants and normalizes rows before scoring.
