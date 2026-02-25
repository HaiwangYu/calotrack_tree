```bash
/sphenix/tg/tg01/commissioning/CaloCalibWG/sli/fm4npp_eval/d9_m5_k30_p20_eval_merged_d70000_1_seed10_per_point_data.csv
/sphenix/tg/tg01/commissioning/CaloCalibWG/sli/fm4npp_eval/d9_m5_k30_p20_eval_merged_d70000_1_seed1_per_point_data.csv
/sphenix/tg/tg01/commissioning/CaloCalibWG/sli/fm4npp_eval/d9_m5_k30_p20_eval_merged_d70000_1_seed2_per_point_data.csv
/sphenix/tg/tg01/commissioning/CaloCalibWG/sli/fm4npp_eval/d9_m5_k30_p20_eval_merged_d70000_1_seed3_per_point_data.csv
/sphenix/tg/tg01/commissioning/CaloCalibWG/sli/fm4npp_eval/d9_m5_k30_p20_eval_merged_d70000_1_seed4_per_point_data.csv
/sphenix/tg/tg01/commissioning/CaloCalibWG/sli/fm4npp_eval/d9_m5_k30_p20_eval_merged_d70000_1_seed5_per_point_data.csv
/sphenix/tg/tg01/commissioning/CaloCalibWG/sli/fm4npp_eval/d9_m5_k30_p20_eval_merged_d70000_1_seed6_per_point_data.csv
/sphenix/tg/tg01/commissioning/CaloCalibWG/sli/fm4npp_eval/d9_m5_k30_p20_eval_merged_d70000_1_seed7_per_point_data.csv
/sphenix/tg/tg01/commissioning/CaloCalibWG/sli/fm4npp_eval/d9_m5_k30_p20_eval_merged_d70000_1_seed8_per_point_data.csv
/sphenix/tg/tg01/commissioning/CaloCalibWG/sli/fm4npp_eval/d9_m5_k30_p20_eval_merged_d70000_1_seed9_per_point_data.csv
```

# Task Name: point to track
## Description
write a python script to convert csv files consist of per-point infomrations into a much smaller files with per-reco-track csv files. Example of input file: /sphenix/user/hwyu/calotrack_tree/macro/dedx-fm/sample.csv
Each row of the input CSV corresponds to a point.
## Rules
- output CSV will have 4 columes: `track_pred_assignment`, `track_energy_majority`, `pid_pred_class_majority`, `pid_true_class_majority`
- only points from the same event (`track_batch_idx`) can be grouped to a reco-track
- within one event (same track_batch_idx), points with the same `track_pred_assignment` belongs to a reco-track. And this `track_pred_assignment` will be used as the per-reco-track `track_pred_assignment`
- within each reco-track, the associated true-track-ID (`track_seg_target`) for each point could be defferent, which means the `track_energy` could also be different, keep counting which `track_energy` is associated with most points, use that `track_energy` as the per-reco-track `track_energy_majority`. Note, this is NOT an averaged `track_energy`. This is the `track_energy` with the most points in that reco-track.
- Similarly, use this majority voting algorithm to form the `pid_pred_class_majority` (majority `pid_pred_class`), `pid_true_class_majority` (majority `pid_true_class`).


# Task: Point-to-Track CSV Aggregation

Write a Python 3 script that converts a per-point CSV into a per-reco-track CSV using majority voting.

## Input
- One CSV file where each row is a point.
- Example input path:
  /sphenix/user/hwyu/calotrack_tree/macro/dedx-fm/sample.csv
- Required input columns (must exist):
  - track_batch_idx            (event id)
  - track_pred_assignment      (predicted track id within an event)
  - track_energy               (point-level energy associated with the true track id)
  - track_seg_target           (true track id; may vary within a reco-track)
  - pid_pred_class             (point-level predicted PID class)
  - pid_true_class             (point-level true PID class)

## Grouping Logic
1) Only points from the same event can be grouped:
   - Group by track_batch_idx first.
2) Within each event, points with the same track_pred_assignment form one reco-track:
   - A reco-track is uniquely identified by (track_batch_idx, track_pred_assignment).

## Output
For each reco-track, write exactly one row to the output CSV with 4 columns:
1) track_pred_assignment
2) track_energy_majority
3) pid_pred_class_majority
4) pid_true_class_majority

Notes:
- track_energy_majority is NOT an average. It is the most frequent track_energy value among the points in the reco-track (majority vote).
- pid_pred_class_majority and pid_true_class_majority are also majority votes over their point-level values.

## Majority Vote Tie-breaking
If there is a tie (two or more values share the highest count), break ties deterministically:
- Choose the smallest value (numeric) or lexicographically smallest (string).
Document this behavior in comments.

## Missing Values
- If a field used for voting has missing/NaN values, ignore NaNs in the vote.
- If all values are NaN for a given vote within a reco-track, output an empty value for that majority column.

## Script Interface
Implement as a command-line tool:

python point_to_track.py \
  --input /path/to/input.csv \
  --output /path/to/output.csv

Optional:
- If --output is not provided, write next to input with suffix: *_per_track.csv

## Implementation Requirements
- Use pandas.
- Validate required columns and exit with a clear error if any are missing.
- Be memory-conscious: support large CSVs by processing in chunks (e.g., pandas.read_csv(chunksize=...)).
- Ensure output is reproducible and stable.

## Deliverables
- point_to_track.py with clear docstring and usage instructions.
- Minimal logging (print progress every N chunks).


```bash
python point_to_track.py \
--input /sphenix/tg/tg01/commissioning/CaloCalibWG/sli/fm4npp_eval/d9_m5_k30_p20_eval_merged_d70000_1_seed1_per_point_data.csv \
--output /sphenix/user/hwyu/calotrack_tree/macro/dedx-fm/seed1_per_track.csv

```